from frame.data.benign import (
    inject_benign_shared_device_groups,
    inject_benign_shared_ip_groups,
)
from frame.data.generator import (
    generate_legitimate_transactions,
)


def test_shared_ip_groups_remain_legitimate() -> None:
    transactions = (
        generate_legitimate_transactions(
            count=500,
            customer_count=100,
            seed=42,
        )
    )

    updated = (
        inject_benign_shared_ip_groups(
            transactions,
            group_count=3,
            customers_per_group=4,
            seed=42,
        )
    )

    assert all(
        not transaction.is_fraud
        for transaction in updated
    )


def test_shared_ip_is_used_by_multiple_customers() -> None:
    transactions = (
        generate_legitimate_transactions(
            count=1000,
            customer_count=100,
            seed=42,
        )
    )

    updated = (
        inject_benign_shared_ip_groups(
            transactions,
            group_count=1,
            customers_per_group=5,
            seed=42,
        )
    )

    shared_ip_transactions = [
        transaction
        for transaction in updated
        if transaction.ip_id.startswith(
            "benign_shared_ip_"
        )
    ]

    customers = {
        transaction.customer_id
        for transaction
        in shared_ip_transactions
    }

    assert len(customers) >= 2


def test_shared_device_is_used_by_multiple_customers() -> None:
    transactions = (
        generate_legitimate_transactions(
            count=1000,
            customer_count=100,
            seed=42,
        )
    )

    updated = (
        inject_benign_shared_device_groups(
            transactions,
            group_count=1,
            customers_per_group=3,
            seed=42,
        )
    )

    shared_transactions = [
        transaction
        for transaction in updated
        if transaction.device_id.startswith(
            "benign_shared_device_"
        )
    ]

    customers = {
        transaction.customer_id
        for transaction
        in shared_transactions
    }

    assert len(customers) >= 2