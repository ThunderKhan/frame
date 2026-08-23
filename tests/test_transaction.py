from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from frame.domain.transaction import Transaction


def test_valid_transaction() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        device_id="device_001",
        card_id="card_001",
        ip_id="ip_001",
        amount=999.0,
        timestamp=datetime.now(UTC),
        account_age_days=120,
    )

    assert transaction.amount == 999.0
    assert transaction.is_fraud is False
    assert transaction.fraud_ring_id is None


def test_transaction_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        Transaction(
            transaction_id="txn_001",
            customer_id="cust_001",
            merchant_id="merchant_001",
            device_id="device_001",
            card_id="card_001",
            ip_id="ip_001",
            amount=0,
            timestamp=datetime.now(UTC),
            account_age_days=120,
        )