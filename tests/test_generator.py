from frame.data.generator import generate_legitimate_transactions


def test_generator_returns_requested_number_of_transactions() -> None:
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


def test_generator_is_reproducible() -> None:
    first = generate_legitimate_transactions(
        count=20,
        seed=123,
    )

    second = generate_legitimate_transactions(
        count=20,
        seed=123,
    )

    assert first == second
    