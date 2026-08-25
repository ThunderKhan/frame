from __future__ import annotations

import networkx as nx
import numpy as np
from sklearn.linear_model import LogisticRegression

from frame.domain.transaction import Transaction
from frame.graph.features import extract_graph_features
from frame.risk.baseline import build_labels

HYBRID_FEATURE_NAMES = [
    "amount",
    "account_age_days",
    "customer_degree",
    "card_degree",
    "device_degree",
    "ip_degree",
    "merchant_degree",
    "component_size",
]


def hybrid_feature_vector(
    transaction: Transaction,
    graph: nx.Graph,
) -> list[float]:
    graph_features = extract_graph_features(
        transaction,
        graph,
    )

    return [
        transaction.amount,
        float(transaction.account_age_days),
        graph_features["customer_degree"],
        graph_features["card_degree"],
        graph_features["device_degree"],
        graph_features["ip_degree"],
        graph_features["merchant_degree"],
        graph_features["component_size"],
    ]


def build_hybrid_feature_matrix(
    transactions: list[Transaction],
    graph: nx.Graph,
) -> np.ndarray:
    return np.asarray(
        [
            hybrid_feature_vector(
                transaction,
                graph,
            )
            for transaction in transactions
        ],
        dtype=float,
    )


def train_hybrid_model(
    transactions: list[Transaction],
    graph: nx.Graph,
) -> LogisticRegression:
    features = build_hybrid_feature_matrix(
        transactions,
        graph,
    )

    labels = build_labels(
        transactions,
    )

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        features,
        labels,
    )

    return model