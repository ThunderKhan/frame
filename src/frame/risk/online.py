from __future__ import annotations

import networkx as nx
import numpy as np
from sklearn.calibration import (
    CalibratedClassifierCV,
)
from sklearn.linear_model import (
    LogisticRegression,
)

from frame.domain.transaction import (
    Transaction,
)
from frame.graph.builder import (
    add_transaction_to_graph,
)
from frame.graph.online import (
    extract_online_graph_features,
    has_cross_customer_graph_evidence,
)
from frame.graph.temporal_online import (
    OnlineTemporalState,
)
from frame.risk.baseline import (
    build_labels,
)


def build_online_graph_evidence_mask(
    transactions: list[Transaction],
) -> np.ndarray:
    ordered = sorted(
        transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    graph = nx.Graph()

    evidence_by_id: dict[
        str,
        bool,
    ] = {}

    for transaction in ordered:
        evidence_by_id[
            transaction.transaction_id
        ] = (
            has_cross_customer_graph_evidence(
                transaction,
                graph,
            )
        )

        add_transaction_to_graph(
            graph,
            transaction,
        )

    return np.asarray(
        [
            evidence_by_id[
                transaction.transaction_id
            ]
            for transaction in transactions
        ],
        dtype=bool,
    )

def build_online_feature_matrix(
    transactions: list[Transaction],
) -> np.ndarray:
    ordered = sorted(
        transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    graph = nx.Graph()
    temporal_state = OnlineTemporalState(
        window_minutes=30
    )

    rows_by_id: dict[
        str,
        list[float],
    ] = {}

    for transaction in ordered:
        graph_features = (
            extract_online_graph_features(
                transaction,
                graph,
            )
        )

        temporal = (
            temporal_state.extract_and_update(
                transaction
            )
        )

        row = [
            transaction.amount,
            float(
                transaction.account_age_days
            ),
            graph_features[
                "customer_degree"
            ],
            graph_features[
                "card_degree"
            ],
            graph_features[
                "device_degree"
            ],
            graph_features[
                "ip_degree"
            ],
            graph_features[
                "merchant_degree"
            ],
            graph_features[
                "component_size"
            ],
            temporal[
                "device_transactions_30m"
            ],
            temporal[
                "ip_transactions_30m"
            ],
            temporal[
                "customer_transactions_30m"
            ],
            temporal[
                "device_customers_30m"
            ],
            temporal[
                "ip_customers_30m"
            ],
            temporal[
                "device_merchants_30m"
            ],
        ]

        rows_by_id[
            transaction.transaction_id
        ] = row

        add_transaction_to_graph(
            graph,
            transaction,
        )

    return np.asarray(
        [
            rows_by_id[
                transaction.transaction_id
            ]
            for transaction in transactions
        ],
        dtype=float,
    )


def train_online_hybrid_model(
    transactions: list[Transaction],
) -> CalibratedClassifierCV:
    features = (
        build_online_feature_matrix(
            transactions
        )
    )

    labels = build_labels(
        transactions
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