from datetime import (
    UTC,
    datetime,
    timedelta,
)

import numpy as np

from frame.domain.transaction import (
    Transaction,
)
from frame.evaluation.latency import (
    evaluate_ring_detection_latency,
)


def make_fraud_transaction(
    index: int,
) -> Transaction:
    return Transaction(
        transaction_id=f"txn_{index:03d}",
        customer_id=f"cust_{index:03d}",
        merchant_id="merchant_001",
        device_id="device_shared",
        card_id=f"card_{index:03d}",
        ip_id="ip_shared",
        amount=500.0,
        timestamp=(
            datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            )
            + timedelta(minutes=index)
        ),
        account_age_days=100,
        is_fraud=True,
        fraud_ring_id="ring_001",
    )


def test_ring_detection_latency() -> None:
    transactions = [
        make_fraud_transaction(
            index
        )
        for index in range(4)
    ]

    probabilities = np.asarray(
        [
            0.10,
            0.20,
            0.80,
            0.90,
        ]
    )

    results = (
        evaluate_ring_detection_latency(
            transactions,
            probabilities,
            threshold=0.50,
        )
    )

    assert len(results) == 1

    result = results[0]

    assert (
        result.transactions_until_detection
        == 3
    )

    assert (
        result.time_until_detection
        == timedelta(minutes=2)
    )