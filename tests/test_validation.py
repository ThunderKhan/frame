from datetime import UTC, datetime

import pytest

from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions
from frame.data.validation import (
    DatasetValidationError,
    validate_dataset,
)
from frame.domain.transaction import Transaction


def test_valid_legitimate_dataset_passes_validation() -> None:
    transactions = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    validate_dataset(transactions)


def test_valid_dataset_with_fraud_ring_passes_validation() -> None:
    legitimate = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    transactions = inject_device_farm(
        legitimate,
        ring_id="ring_test",
        ring_size=5,
        transactions_per_account=2,
        seed=42,
    )

    validate_dataset(transactions)


def test_empty_dataset_is_rejected() -> None:
    with pytest.raises(DatasetValidationError):
        validate_dataset([])


def test_duplicate_transaction_ids_are_rejected() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        device_id="device_001",
        card_id="card_001",
        ip_id="ip_001",
        amount=999.0,
        timestamp=datetime.now(UTC),
        account_age_days=100,
    )

    transactions = [
        transaction,
        transaction.model_copy(),
    ]

    with pytest.raises(
        DatasetValidationError,
        match="Duplicate transaction IDs",
    ):
        validate_dataset(transactions)


def test_fraud_without_ring_id_is_rejected() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        device_id="device_001",
        card_id="card_001",
        ip_id="ip_001",
        amount=999.0,
        timestamp=datetime.now(UTC),
        account_age_days=3,
        is_fraud=True,
        fraud_ring_id=None,
    )

    with pytest.raises(
        DatasetValidationError,
        match="Inconsistent fraud labels",
    ):
        validate_dataset([transaction])


def test_legitimate_transaction_with_ring_id_is_rejected() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        customer_id="cust_001",
        merchant_id="merchant_001",
        device_id="device_001",
        card_id="card_001",
        ip_id="ip_001",
        amount=999.0,
        timestamp=datetime.now(UTC),
        account_age_days=200,
        is_fraud=False,
        fraud_ring_id="ring_001",
    )

    with pytest.raises(
        DatasetValidationError,
        match="Inconsistent fraud labels",
    ):
        validate_dataset([transaction])


def test_single_customer_fraud_ring_is_rejected() -> None:
    transactions = [
        Transaction(
            transaction_id=f"txn_{index:03d}",
            customer_id="fraud_customer_001",
            merchant_id="merchant_001",
            device_id="fraud_device_001",
            card_id="fraud_card_001",
            ip_id="fraud_ip_001",
            amount=1000.0,
            timestamp=datetime.now(UTC),
            account_age_days=2,
            is_fraud=True,
            fraud_ring_id="ring_001",
        )
        for index in range(3)
    ]

    with pytest.raises(
        DatasetValidationError,
        match="Fraud rings must contain multiple customers",
    ):
        validate_dataset(transactions)