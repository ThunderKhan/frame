from __future__ import annotations

import networkx as nx
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

from frame.domain.transaction import Transaction
from frame.graph.features import extract_graph_features
from frame.graph.temporal import build_temporal_features
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
    "device_transactions_30m",
    "ip_transactions_30m",
    "customer_transactions_30m",
    "device_customers_30m",
    "ip_customers_30m",
    "device_merchants_30m",
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
    temporal_features = build_temporal_features(
        transactions
    )

    rows: list[list[float]] = []

    for transaction in transactions:
        graph_features = extract_graph_features(
            transaction,
            graph,
        )

        temporal = temporal_features[
            transaction.transaction_id
        ]

        rows.append(
            [
                transaction.amount,
                float(transaction.account_age_days),
                graph_features["customer_degree"],
                graph_features["card_degree"],
                graph_features["device_degree"],
                graph_features["ip_degree"],
                graph_features["merchant_degree"],
                graph_features["component_size"],
                temporal["device_transactions_30m"],
                temporal["ip_transactions_30m"],
                temporal["customer_transactions_30m"],
                temporal["device_customers_30m"],
                temporal["ip_customers_30m"],
                temporal["device_merchants_30m"],
            ]
        )

    return np.asarray(
        rows,
        dtype=float,
    )

def train_hybrid_model(
    transactions: list[Transaction],
    graph: nx.Graph,
) -> CalibratedClassifierCV:
    features = build_hybrid_feature_matrix(
        transactions,
        graph,
    )

    labels = build_labels(
        transactions,
    )

    base_model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )

    model = CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=5,
    )

    model.fit(
        features,
        labels,
    )

    return model