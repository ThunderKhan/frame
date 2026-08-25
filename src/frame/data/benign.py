from __future__ import annotations

from random import Random

from frame.domain.transaction import Transaction


def inject_benign_shared_ip_groups(
    transactions: list[Transaction],
    group_count: int = 5,
    customers_per_group: int = 6,
    seed: int = 42,
) -> list[Transaction]:
    if not transactions:
        raise ValueError("transactions must not be empty")

    if group_count < 1:
        raise ValueError("group_count must be at least 1")

    if customers_per_group < 2:
        raise ValueError("customers_per_group must be at least 2")

    rng = Random(seed)
    output = list(transactions)

    legitimate = [
        transaction
        for transaction in output
        if not transaction.is_fraud
    ]

    customer_ids = sorted(
        {
            transaction.customer_id
            for transaction in legitimate
        }
    )

    required_customers = (
        group_count * customers_per_group
    )

    if len(customer_ids) < required_customers:
        raise ValueError(
            "not enough legitimate customers "
            "for requested shared-IP groups"
        )

    selected_customers = rng.sample(
        customer_ids,
        required_customers,
    )

    customer_to_ip: dict[str, str] = {}

    for group_index in range(group_count):
        start = (
            group_index
            * customers_per_group
        )

        end = start + customers_per_group

        group_customers = selected_customers[
            start:end
        ]

        shared_ip = (
            f"benign_shared_ip_{group_index + 1:03d}"
        )

        for customer_id in group_customers:
            customer_to_ip[
                customer_id
            ] = shared_ip

    updated: list[Transaction] = []

    for transaction in output:
        shared_ip = customer_to_ip.get(
            transaction.customer_id
        )

        if shared_ip is None:
            updated.append(transaction)
            continue

        updated.append(
            transaction.model_copy(
                update={
                    "ip_id": shared_ip,
                }
            )
        )

    return updated


def inject_benign_shared_device_groups(
    transactions: list[Transaction],
    group_count: int = 3,
    customers_per_group: int = 3,
    seed: int = 84,
) -> list[Transaction]:
    if not transactions:
        raise ValueError(
            "transactions must not be empty"
        )

    legitimate = [
        transaction
        for transaction in transactions
        if not transaction.is_fraud
    ]

    customer_ids = sorted(
        {
            transaction.customer_id
            for transaction in legitimate
        }
    )

    required_customers = (
        group_count * customers_per_group
    )

    if len(customer_ids) < required_customers:
        raise ValueError(
            "not enough legitimate customers "
            "for requested shared-device groups"
        )

    rng = Random(seed)

    selected_customers = rng.sample(
        customer_ids,
        required_customers,
    )

    customer_to_device: dict[str, str] = {}

    for group_index in range(group_count):
        start = (
            group_index
            * customers_per_group
        )

        end = start + customers_per_group

        shared_device = (
            f"benign_shared_device_"
            f"{group_index + 1:03d}"
        )

        for customer_id in selected_customers[
            start:end
        ]:
            customer_to_device[
                customer_id
            ] = shared_device

    updated: list[Transaction] = []

    for transaction in transactions:
        shared_device = (
            customer_to_device.get(
                transaction.customer_id
            )
        )

        if shared_device is None:
            updated.append(transaction)
            continue

        updated.append(
            transaction.model_copy(
                update={
                    "device_id": shared_device,
                }
            )
        )

    return updated