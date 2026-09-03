from dataclasses import dataclass
from io import StringIO
from itertools import combinations
from typing import Any
from uuid import uuid4

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score

MAX_UPLOAD_BYTES = 5_000_000
MAX_ROWS = 10_000
MAX_GRAPH_NODES = 800
MAX_RESULTS = 100
MAX_STREAM_EVENTS = 500


@dataclass(frozen=True)
class EntityColumn:
    column: str
    entity_type: str


@dataclass(frozen=True)
class AnalysisMapping:
    entities: tuple[EntityColumn, ...]
    transaction_id: str | None = None
    timestamp: str | None = None
    amount: str | None = None
    label: str | None = None


def _string_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text or None


def _numeric_value(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0

    if not np.isfinite(number):
        return 0.0

    return number


def _label_value(value: Any) -> int | None:
    if pd.isna(value):
        return None

    text = str(value).strip().lower()
    if text in {"1", "true", "fraud", "fraudulent", "illicit", "laundering", "yes"}:
        return 1
    if text in {"0", "false", "clean", "legit", "licit", "legitimate", "no"}:
        return 0

    try:
        number = int(float(text))
    except (TypeError, ValueError):
        return None

    return 1 if number != 0 else 0


def _validate_mapping(frame: pd.DataFrame, mapping: AnalysisMapping) -> None:
    required = {entity.column for entity in mapping.entities}

    for optional in (
        mapping.transaction_id,
        mapping.timestamp,
        mapping.amount,
        mapping.label,
    ):
        if optional:
            required.add(optional)

    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError("missing mapped columns: " + ", ".join(missing))

    if len(mapping.entities) < 2:
        raise ValueError("relationship analysis requires at least two mapped entity columns")


def _build_relationship_graph(
    frame: pd.DataFrame,
    mapping: AnalysisMapping,
) -> tuple[nx.Graph, list[list[str]], list[float]]:
    graph = nx.Graph()
    row_nodes: list[list[str]] = []
    row_amounts: list[float] = []

    for _, row in frame.iterrows():
        nodes: list[str] = []

        for entity in mapping.entities:
            value = _string_value(row[entity.column])
            if value is None:
                continue

            node_id = f"{entity.entity_type}:{value}"
            nodes.append(node_id)

            if node_id not in graph:
                graph.add_node(
                    node_id,
                    id=node_id,
                    label=value,
                    type=entity.entity_type,
                )

        nodes = list(dict.fromkeys(nodes))
        amount = _numeric_value(row[mapping.amount]) if mapping.amount else 0.0

        for left, right in combinations(nodes, 2):
            if graph.has_edge(left, right):
                graph[left][right]["transactions"] += 1
                graph[left][right]["amount"] += amount
            else:
                graph.add_edge(
                    left,
                    right,
                    transactions=1,
                    amount=amount,
                )

        row_nodes.append(nodes)
        row_amounts.append(amount)

    return graph, row_nodes, row_amounts


def _component_sizes(graph: nx.Graph) -> dict[str, int]:
    result: dict[str, int] = {}

    for component in nx.connected_components(graph):
        size = len(component)
        for node_id in component:
            result[node_id] = size

    return result


def _row_features(
    graph: nx.Graph,
    row_nodes: list[list[str]],
    row_amounts: list[float],
) -> np.ndarray:
    component_sizes = _component_sizes(graph)
    feature_rows: list[list[float]] = []

    for nodes, amount in zip(row_nodes, row_amounts, strict=True):
        degrees = [
            float(graph.degree(node_id))
            for node_id in nodes
            if node_id in graph
        ]

        component = [float(component_sizes.get(node_id, 1)) for node_id in nodes]

        pair_weights: list[float] = []
        for left, right in combinations(nodes, 2):
            if graph.has_edge(left, right):
                pair_weights.append(float(graph[left][right].get("transactions", 1)))

        feature_rows.append(
            [
                float(np.log1p(max(amount, 0.0))),
                max(degrees, default=0.0),
                float(np.mean(degrees)) if degrees else 0.0,
                max(component, default=1.0),
                max(pair_weights, default=0.0),
                float(len(nodes)),
            ]
        )

    return np.asarray(feature_rows, dtype=float)


def _anomaly_scores(features: np.ndarray) -> np.ndarray:
    if len(features) < 20:
        return np.zeros(len(features), dtype=float)

    model = IsolationForest(
        n_estimators=150,
        contamination="auto",
        random_state=42,
        n_jobs=1,
    )
    model.fit(features)

    raw = -model.score_samples(features)
    ranks = pd.Series(raw).rank(method="average", pct=True)
    return ranks.to_numpy(dtype=float)


def _graph_payload(graph: nx.Graph) -> dict[str, Any]:
    ordered = sorted(
        graph.nodes,
        key=lambda node_id: graph.degree(node_id),
        reverse=True,
    )
    kept = set(ordered[:MAX_GRAPH_NODES])

    nodes = [
        {
            "id": node_id,
            "attributes": {
                "node_type": graph.nodes[node_id].get("type", "entity"),
                "entity_id": graph.nodes[node_id].get("label", node_id),
                "degree": graph.degree(node_id),
            },
        }
        for node_id in ordered[:MAX_GRAPH_NODES]
    ]

    edges = [
        {
            "source": left,
            "target": right,
            "attributes": {
                "relation": "dataset_relationship",
                "transactions": data.get("transactions", 1),
                "amount": round(float(data.get("amount", 0.0)), 2),
            },
        }
        for left, right, data in graph.edges(data=True)
        if left in kept and right in kept
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "truncated": graph.number_of_nodes() > MAX_GRAPH_NODES,
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
    }


def analyze_csv(
    *,
    dataset_id: str,
    filename: str,
    csv_text: str,
    mapping: AnalysisMapping,
    row_limit: int,
) -> dict[str, Any]:
    encoded_size = len(csv_text.encode("utf-8"))
    if encoded_size > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"public demo uploads are capped at {MAX_UPLOAD_BYTES // 1_000_000} MB"
        )

    bounded_limit = min(max(row_limit, 1), MAX_ROWS)

    try:
        frame = pd.read_csv(
            StringIO(csv_text),
            nrows=bounded_limit,
        )
    except Exception as exc:
        raise ValueError("unable to parse CSV") from exc

    if frame.empty:
        raise ValueError("dataset contains no rows")

    _validate_mapping(frame, mapping)

    graph, row_nodes, row_amounts = _build_relationship_graph(
        frame,
        mapping,
    )

    features = _row_features(
        graph,
        row_nodes,
        row_amounts,
    )
    scores = _anomaly_scores(features)

    labels: list[int | None] = []
    if mapping.label:
        labels = [_label_value(value) for value in frame[mapping.label].tolist()]
    else:
        labels = [None] * len(frame)

    results: list[dict[str, Any]] = []
    for position, (_, row) in enumerate(frame.iterrows()):
        transaction_id = (
            _string_value(row[mapping.transaction_id]) if mapping.transaction_id else None
        ) or f"row_{position + 1}"

        results.append(
            {
                "transaction_id": transaction_id,
                "row": position + 1,
                "anomaly_score": float(scores[position]),
                "amount": row_amounts[position],
                "label": labels[position],
                "entities": row_nodes[position],
            }
        )

    stream_events = [
        {
            "transaction_id": item["transaction_id"],
            "row": item["row"],
            "amount": item["amount"],
            "label": item["label"],
            "entities": item["entities"],
        }
        for item in results[:MAX_STREAM_EVENTS]
    ]

    results.sort(
        key=lambda item: item["anomaly_score"],
        reverse=True,
    )

    components = list(nx.connected_components(graph))
    largest_component = max(
        (len(component) for component in components),
        default=0,
    )

    evaluation: dict[str, Any] | None = None
    known_pairs = [
        (label, float(scores[index]))
        for index, label in enumerate(labels)
        if label is not None
    ]

    if known_pairs:
        y_true = np.asarray(
            [pair[0] for pair in known_pairs],
            dtype=int,
        )
        y_score = np.asarray(
            [pair[1] for pair in known_pairs],
            dtype=float,
        )

        evaluation = {
            "labeled_rows": len(y_true),
            "positive_labels": int(y_true.sum()),
        }

        if len(np.unique(y_true)) == 2:
            evaluation["anomaly_pr_auc"] = float(
                average_precision_score(y_true, y_score)
            )
            evaluation["anomaly_roc_auc"] = float(
                roc_auc_score(y_true, y_score)
            )

    return {
        "analysis_id": uuid4().hex,
        "dataset_id": dataset_id,
        "filename": filename,
        "analysis_mode": "relational_graph_unsupervised",
        "model": {
            "name": "IsolationForest",
            "purpose": (
                "Unsupervised relationship-anomaly ranking over graph-derived "
                "row features. This is not the FRAME online fraud probability model."
            ),
            "features": [
                "log_amount",
                "max_entity_degree",
                "mean_entity_degree",
                "max_component_size",
                "max_pair_transaction_count",
                "entity_count",
            ],
        },
        "summary": {
            "rows_analyzed": len(frame),
            "columns": len(frame.columns),
            "graph_nodes": graph.number_of_nodes(),
            "graph_edges": graph.number_of_edges(),
            "components": len(components),
            "largest_component": largest_component,
            "entity_types": sorted(
                {entity.entity_type for entity in mapping.entities}
            ),
        },
        "evaluation": evaluation,
        "graph": _graph_payload(graph),
        "stream_events": stream_events,
        "top_anomalies": results[:MAX_RESULTS],
    }
