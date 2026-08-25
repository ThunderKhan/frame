import numpy as np

from frame.domain.transaction import Transaction
from frame.evaluation.hard_negatives import (
    evaluate_hard_negatives,
)


def test_hard_negative_false_positive_rates() -> None:
    from datetime import UTC, datetime

    transactions = [
        Transaction(
            transaction_id="txn_001",
            customer_id="cust_001",
            merchant_id="merchant_001",
            device_id="device_001",
            card_id="card_001",
            ip_id="benign_shared_ip_001",
            amount=500.0,
            timestamp=datetime.now(UTC),
            account_age_days=200,
        ),
        Transaction(
            transaction_id="txn_002",
            customer_id="cust_002",
            merchant_id="merchant_001",
            device_id="benign_shared_device_001",
            card_id="card_002",
            ip_id="ip_002",
            amount=700.0,
            timestamp=datetime.now(UTC),
            account_age_days=300,
        ),
    ]

    probabilities = np.asarray(
        [0.8, 0.2]
    )

    metrics = evaluate_hard_negatives(
        transactions,
        probabilities,
        threshold=0.5,
    )

    assert metrics.shared_ip_count == 1
    assert metrics.shared_ip_flagged == 1
    assert (
        metrics.shared_ip_false_positive_rate
        == 1.0
    )

    assert metrics.shared_device_count == 1
    assert metrics.shared_device_flagged == 0
    assert (
        metrics.shared_device_false_positive_rate
        == 0.0
    )