from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from frame.domain.transaction import Transaction


@dataclass(frozen=True)
class HardNegativeMetrics:
    shared_ip_count: int
    shared_ip_flagged: int
    shared_ip_false_positive_rate: float

    shared_device_count: int
    shared_device_flagged: int
    shared_device_false_positive_rate: float


def evaluate_hard_negatives(
    transactions: list[Transaction],
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> HardNegativeMetrics:
    if len(transactions) != len(probabilities):
        raise ValueError(
            "transactions and probabilities must have equal length"
        )

    predictions = (
        probabilities >= threshold
    ).astype(int)

    shared_ip_indices = [
        index
        for index, transaction
        in enumerate(transactions)
        if (
            not transaction.is_fraud
            and transaction.ip_id.startswith(
                "benign_shared_ip_"
            )
        )
    ]

    shared_device_indices = [
        index
        for index, transaction
        in enumerate(transactions)
        if (
            not transaction.is_fraud
            and transaction.device_id.startswith(
                "benign_shared_device_"
            )
        )
    ]

    shared_ip_flagged = sum(
        int(predictions[index])
        for index in shared_ip_indices
    )

    shared_device_flagged = sum(
        int(predictions[index])
        for index in shared_device_indices
    )

    shared_ip_count = len(
        shared_ip_indices
    )

    shared_device_count = len(
        shared_device_indices
    )

    shared_ip_fpr = (
        shared_ip_flagged
        / shared_ip_count
        if shared_ip_count
        else 0.0
    )

    shared_device_fpr = (
        shared_device_flagged
        / shared_device_count
        if shared_device_count
        else 0.0
    )

    return HardNegativeMetrics(
        shared_ip_count=shared_ip_count,
        shared_ip_flagged=shared_ip_flagged,
        shared_ip_false_positive_rate=(
            shared_ip_fpr
        ),
        shared_device_count=(
            shared_device_count
        ),
        shared_device_flagged=(
            shared_device_flagged
        ),
        shared_device_false_positive_rate=(
            shared_device_fpr
        ),
    )