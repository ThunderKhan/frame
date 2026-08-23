import pytest

from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions


def test_device_farm_adds_expected_number_of_transactions() -> None:
    legitimate = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    result = inject_device_farm(
        legitimate,
        ring_size=5,
        transactions_per_account=3,
        seed=42,
    )

    assert len(result) == 115


def test_injected_transactions_are_labeled_as_fraud() -> None:
    legitimate = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    result = inject_device_farm(
        legitimate,
        ring_id="ring_test",
        ring_size=4,
        transactions_per_account=2,
        seed=42,
    )

    injected = result[len(legitimate):]

    assert len(injected) == 8
    assert all(transaction.is_fraud for transaction in injected)
    assert all(
        transaction.fraud_ring_id == "ring_test"
        for transaction in injected
    )


def test_device_farm_shares_device_and_ip() -> None:
    legitimate = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    result = inject_device_farm(
        legitimate,
        ring_id="ring_shared",
        ring_size=5,
        transactions_per_account=2,
        seed=42,
    )

    injected = result[len(legitimate):]

    device_ids = {
        transaction.device_id
        for transaction in injected
    }

    ip_ids = {
        transaction.ip_id
        for transaction in injected
    }

    assert len(device_ids) == 1
    assert len(ip_ids) == 1


def test_device_farm_contains_multiple_customers() -> None:
    legitimate = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    result = inject_device_farm(
        legitimate,
        ring_size=6,
        transactions_per_account=2,
        seed=42,
    )

    injected = result[len(legitimate):]

    customer_ids = {
        transaction.customer_id
        for transaction in injected
    }

    assert len(customer_ids) == 6


def test_existing_transactions_are_not_modified() -> None:
    legitimate = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    original = [transaction.model_copy() for transaction in legitimate]

    inject_device_farm(
        legitimate,
        ring_size=5,
        transactions_per_account=2,
        seed=42,
    )

    assert legitimate == original


def test_device_farm_is_reproducible() -> None:
    legitimate = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    first = inject_device_farm(
        legitimate,
        ring_size=5,
        transactions_per_account=3,
        seed=123,
    )

    second = inject_device_farm(
        legitimate,
        ring_size=5,
        transactions_per_account=3,
        seed=123,
    )

    assert first == second


def test_device_farm_rejects_empty_input() -> None:
    with pytest.raises(ValueError):
        inject_device_farm([])


def test_device_farm_requires_multiple_accounts() -> None:
    legitimate = generate_legitimate_transactions(
        count=20,
        seed=42,
    )

    with pytest.raises(ValueError):
        inject_device_farm(
            legitimate,
            ring_size=1,
        )