from frame.evaluation.worlds import (
    build_hard_negative_world,
)


def test_hard_negative_world_contains_benign_shared_ips() -> None:
    world = build_hard_negative_world(
        legitimate_count=1000,
        ring_count=2,
        ring_size=5,
        transactions_per_account=2,
        seed=42,
        shared_ip_group_count=3,
        shared_ip_customers_per_group=4,
    )

    shared_ip_transactions = [
        transaction
        for transaction in world.transactions
        if transaction.ip_id.startswith(
            "benign_shared_ip_"
        )
    ]

    assert shared_ip_transactions

    assert all(
        not transaction.is_fraud
        for transaction in shared_ip_transactions
    )


def test_hard_negative_world_contains_benign_shared_devices() -> None:
    world = build_hard_negative_world(
        legitimate_count=1000,
        ring_count=2,
        ring_size=5,
        transactions_per_account=2,
        seed=42,
        shared_device_group_count=3,
        shared_device_customers_per_group=3,
    )

    shared_device_transactions = [
        transaction
        for transaction in world.transactions
        if transaction.device_id.startswith(
            "benign_shared_device_"
        )
    ]

    assert shared_device_transactions

    assert all(
        not transaction.is_fraud
        for transaction
        in shared_device_transactions
    )


def test_hard_negative_world_still_contains_fraud() -> None:
    world = build_hard_negative_world(
        legitimate_count=1000,
        ring_count=2,
        ring_size=5,
        transactions_per_account=2,
        seed=42,
    )

    fraud_transactions = [
        transaction
        for transaction in world.transactions
        if transaction.is_fraud
    ]

    assert fraud_transactions