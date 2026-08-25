from datetime import UTC, datetime, timedelta

from frame.domain.transaction import Transaction
from frame.graph.temporal import build_temporal_features


def test_temporal_features_detect_shared_device_burst() -> None:
    base_time = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )

    transactions = [
        Transaction(
            transaction_id=f"txn_{index:03d}",
            customer_id=f"cust_{index:03d}",
            merchant_id="merchant_001",
            device_id="device_shared",
            card_id=f"card_{index:03d}",
            ip_id="ip_shared",
            amount=500.0,
            timestamp=base_time
            + timedelta(minutes=index * 2),
            account_age_days=100,
        )
        for index in range(5)
    ]

    features = build_temporal_features(
        transactions,
        window_minutes=30,
    )

    last = features["txn_004"]

    assert last["device_transactions_30m"] == 5.0
    assert last["device_customers_30m"] == 5.0
    assert last["ip_customers_30m"] == 5.0