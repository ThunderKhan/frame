from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np
from sklearn.linear_model import (
    LogisticRegression,
)

from frame.domain.transaction import (
    Transaction,
)
from frame.evaluation.metrics import (
    EvaluationMetrics,
    evaluate_predictions,
)
from frame.graph.features import (
    extract_graph_features,
)
from frame.risk.baseline import (
    build_labels,
)


@dataclass(frozen=True)
class AblationResult:
    name: str
    metrics: EvaluationMetrics


def build_selected_feature_matrix(
    transactions: list[Transaction],
    graph: nx.Graph,
    graph_feature_names: list[str],
) -> np.ndarray:
    rows: list[list[float]] = []

    for transaction in transactions:
        graph_features = (
            extract_graph_features(
                transaction,
                graph,
            )
        )

        row = [
            transaction.amount,
            float(
                transaction
                .account_age_days
            ),
        ]

        row.extend(
            graph_features[name]
            for name
            in graph_feature_names
        )

        rows.append(row)

    return np.asarray(
        rows,
        dtype=float,
    )


def evaluate_ablation(
    name: str,
    train_transactions: list[Transaction],
    test_transactions: list[Transaction],
    train_graph: nx.Graph,
    test_graph: nx.Graph,
    graph_feature_names: list[str],
) -> AblationResult:
    train_features = (
        build_selected_feature_matrix(
            train_transactions,
            train_graph,
            graph_feature_names,
        )
    )

    test_features = (
        build_selected_feature_matrix(
            test_transactions,
            test_graph,
            graph_feature_names,
        )
    )

    train_labels = build_labels(
        train_transactions
    )

    test_labels = build_labels(
        test_transactions
    )

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        train_features,
        train_labels,
    )

    predictions = model.predict(
        test_features
    )

    probabilities = (
        model.predict_proba(
            test_features
        )[:, 1]
    )

    metrics = evaluate_predictions(
        test_labels,
        predictions,
        probabilities,
    )

    return AblationResult(
        name=name,
        metrics=metrics,
    )