from __future__ import annotations

from collections import Counter

from frame.domain.transaction import Transaction


class DatasetValidationError(ValueError):
    """Raised when generated transaction data violates an invariant."""


def validate_unique_transaction_ids(
    transactions: list[Transaction],
) -> None:
    transaction_ids = [
        transaction.transaction_id
        for transaction in transactions
    ]

    counts = Counter(transaction_ids)

    duplicates = [
        transaction_id
        for transaction_id, count in counts.items()
        if count > 1
    ]

    if duplicates:
        raise DatasetValidationError(
            f"Duplicate transaction IDs found: {duplicates}"
        )


def validate_positive_amounts(
    transactions: list[Transaction],
) -> None:
    invalid = [
        transaction.transaction_id
        for transaction in transactions
        if transaction.amount <= 0
    ]

    if invalid:
        raise DatasetValidationError(
            f"Transactions with non-positive amounts found: {invalid}"
        )


def validate_fraud_labels(
    transactions: list[Transaction],
) -> None:
    invalid = []

    for transaction in transactions:
        if transaction.is_fraud and transaction.fraud_ring_id is None:
            invalid.append(transaction.transaction_id)

        if not transaction.is_fraud and transaction.fraud_ring_id is not None:
            invalid.append(transaction.transaction_id)

    if invalid:
        raise DatasetValidationError(
            "Inconsistent fraud labels found for transactions: "
            f"{invalid}"
        )


def validate_fraud_rings_have_multiple_customers(
    transactions: list[Transaction],
) -> None:
    ring_customers: dict[str, set[str]] = {}

    for transaction in transactions:
        if not transaction.is_fraud:
            continue

        assert transaction.fraud_ring_id is not None

        ring_customers.setdefault(
            transaction.fraud_ring_id,
            set(),
        ).add(transaction.customer_id)

    invalid_rings = [
        ring_id
        for ring_id, customer_ids in ring_customers.items()
        if len(customer_ids) < 2
    ]

    if invalid_rings:
        raise DatasetValidationError(
            "Fraud rings must contain multiple customers: "
            f"{invalid_rings}"
        )


def validate_dataset(
    transactions: list[Transaction],
) -> None:
    if not transactions:
        raise DatasetValidationError(
            "Dataset must contain at least one transaction."
        )

    validate_unique_transaction_ids(transactions)
    validate_positive_amounts(transactions)
    validate_fraud_labels(transactions)
    validate_fraud_rings_have_multiple_customers(transactions)