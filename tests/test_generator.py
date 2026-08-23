from frame.data.generator import (
    generate_customer_profiles,
    generate_legitimate_transactions,
)


def test_customer_generator_returns_requested_count() -> None:
    customers = generate_customer_profiles(
        count=100,
        seed=42,
    )

    assert len(customers) == 100


def test_customer_profiles_are_reproducible() -> None:
    first = generate_customer_profiles(
        count=20,
        seed=123,
    )

    second = generate_customer_profiles(
        count=20,
        seed=123,
    )

    assert first == second


def test_legitimate_transaction_count() -> None:
    transactions = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    assert len(transactions) == 100


def test_generated_transactions_are_legitimate() -> None:
    transactions = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    assert all(transaction.is_fraud is False for transaction in transactions)
    assert all(transaction.fraud_ring_id is None for transaction in transactions)


def test_legitimate_transactions_are_reproducible() -> None:
    first = generate_legitimate_transactions(
        count=50,
        seed=123,
    )

    second = generate_legitimate_transactions(
        count=50,
        seed=123,
    )

    assert first == second


def test_transactions_use_customer_owned_entities() -> None:
    customers = generate_customer_profiles(
        count=50,
        seed=42,
    )

    customer_lookup = {
        customer.customer_id: customer
        for customer in customers
    }

    transactions = generate_legitimate_transactions(
        count=200,
        customer_count=50,
        seed=42,
    )

    for transaction in transactions:
        customer = customer_lookup[transaction.customer_id]

        assert transaction.card_id in customer.card_ids
        assert transaction.device_id in customer.device_ids
        assert transaction.ip_id in customer.ip_ids