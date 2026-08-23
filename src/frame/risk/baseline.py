from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

from frame.domain.transaction import Transaction

TRANSACTION_FEATURE_NAMES = [
    "amount",
    "account_age_days",
]


def transaction_feature_vector(
    transaction: Transaction,
) -> list[float]:
    return [
        transaction.amount,
        float(transaction.account_age_days),
    ]


def build_transaction_feature_matrix(
    transactions: list[Transaction],
) -> np.ndarray:
    return np.asarray(
        [
            transaction_feature_vector(transaction)
            for transaction in transactions
        ],
        dtype=float,
    )


def build_labels(
    transactions: list[Transaction],
) -> np.ndarray:
    return np.asarray(
        [
            int(transaction.is_fraud)
            for transaction in transactions
        ],
        dtype=int,
    )


def train_transaction_baseline(
    transactions: list[Transaction],
) -> LogisticRegression:
    features = build_transaction_feature_matrix(
        transactions,
    )
    labels = build_labels(
        transactions,
    )

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        features,
        labels,
    )

    return model