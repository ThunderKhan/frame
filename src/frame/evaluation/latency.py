from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import numpy as np

from frame.domain.transaction import (
    Transaction,
)


@dataclass(frozen=True)
class RingDetectionLatency:
    ring_id: str
    fraud_transactions: int
    first_fraud_index: int
    first_detection_index: int | None
    transactions_until_detection: int | None
    time_until_detection: timedelta | None


def evaluate_ring_detection_latency(
    transactions: list[Transaction],
    probabilities: np.ndarray,
    threshold: float,
) -> list[RingDetectionLatency]:
    if len(transactions) != len(probabilities):
        raise ValueError(
            "transactions and probabilities must have equal length"
        )

    indexed = list(
        zip(
            transactions,
            probabilities,
            strict=True,
        )
    )

    indexed.sort(
        key=lambda item: (
            item[0].timestamp,
            item[0].transaction_id,
        )
    )

    ring_ids = sorted(
        {
            transaction.fraud_ring_id
            for transaction, _ in indexed
            if (
                transaction.is_fraud
                and transaction.fraud_ring_id
                is not None
            )
        }
    )

    results: list[
        RingDetectionLatency
    ] = []

    for ring_id in ring_ids:
        ring_transactions = [
            (
                global_index,
                transaction,
                float(probability),
            )
            for global_index, (
                transaction,
                probability,
            ) in enumerate(indexed)
            if transaction.fraud_ring_id == ring_id
        ]

        first_index = (
            ring_transactions[0][0]
        )

        first_transaction = (
            ring_transactions[0][1]
        )

        detected = [
            item
            for item in ring_transactions
            if item[2] >= threshold
        ]

        if detected:
            detection_index = (
                detected[0][0]
            )

            detection_transaction = (
                detected[0][1]
            )

            ring_position = next(
                index
                for index, item
                in enumerate(
                    ring_transactions,
                    start=1,
                )
                if item[0]
                == detection_index
            )

            delay = (
                detection_transaction.timestamp
                - first_transaction.timestamp
            )

            transactions_until_detection = (
                ring_position
            )
        else:
            detection_index = None
            delay = None
            transactions_until_detection = (
                None
            )

        results.append(
            RingDetectionLatency(
                ring_id=ring_id,
                fraud_transactions=len(
                    ring_transactions
                ),
                first_fraud_index=first_index,
                first_detection_index=(
                    detection_index
                ),
                transactions_until_detection=(
                    transactions_until_detection
                ),
                time_until_detection=delay,
            )
        )

    return results