from datetime import UTC, datetime

from frame.domain.transaction import Transaction
from frame.risk.online import (
    ONLINE_FEATURE_NAMES,
    build_online_feature_row,
)


def test_selected_online_schema_excludes_ip_degree() -> None:
    assert "ip_degree" not in ONLINE_FEATURE_NAMES
    assert len(ONLINE_FEATURE_NAMES) == 13


def test_online_feature_row_matches_schema() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        device_id="device_001",
        card_id="card_001",
        ip_id="ip_001",
        amount=500.0,
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        account_age_days=100,
    )

    graph_features = {
        "customer_degree": 1.0,
        "card_degree": 1.0,
        "device_degree": 2.0,
        "ip_degree": 9.0,
        "merchant_degree": 4.0,
        "component_size": 20.0,
    }

    temporal_features = {
        "device_transactions_30m": 3.0,
        "ip_transactions_30m": 4.0,
        "customer_transactions_30m": 2.0,
        "device_customers_30m": 2.0,
        "ip_customers_30m": 3.0,
        "device_merchants_30m": 2.0,
    }

    row = build_online_feature_row(
        transaction,
        graph_features,
        temporal_features,
    )

    assert len(row) == len(
        ONLINE_FEATURE_NAMES
    )

    assert 9.0 not in row