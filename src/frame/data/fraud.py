from __future__ import annotations

from datetime import timedelta
from random import Random

from frame.domain.transaction import Transaction


def inject_device_farm(
    transactions: list[Transaction],
    ring_id: str = "ring_001",
    ring_size: int = 5,
    transactions_per_account: int = 3,
    seed: int = 42,
    shared_device_ratio: float = 1.0,
    shared_ip_ratio: float = 1.0,
) -> list[Transaction]:
    if not transactions:
        raise ValueError("transactions must not be empty")

    if ring_size < 2:
        raise ValueError("ring_size must be at least 2")

    if transactions_per_account < 1:
        raise ValueError("transactions_per_account must be at least 1")

    if not 0.0 <= shared_device_ratio <= 1.0:
        raise ValueError("shared_device_ratio must be between 0 and 1")

    if not 0.0 <= shared_ip_ratio <= 1.0:
        raise ValueError("shared_ip_ratio must be between 0 and 1")

    rng = Random(seed)

    output = list(transactions)

    start_time = max(
        transaction.timestamp
        for transaction in transactions
    )

    shared_device_id = f"fraud_device_{ring_id}"
    shared_ip_id = f"fraud_ip_{ring_id}"

    for account_index in range(1, ring_size + 1):
        customer_id = (
            f"fraud_customer_{ring_id}_{account_index:03d}"
        )

        card_id = (
            f"fraud_card_{ring_id}_{account_index:03d}"
        )

        # Important:
        # Fraud account ages now overlap legitimate accounts.
        account_age_days = rng.randint(
            30,
            1500,
        )

        uses_shared_device = (
            rng.random() < shared_device_ratio
        )

        uses_shared_ip = (
            rng.random() < shared_ip_ratio
        )

        device_id = (
            shared_device_id
            if uses_shared_device
            else f"fraud_device_{ring_id}_{account_index:03d}"
        )

        ip_id = (
            shared_ip_id
            if uses_shared_ip
            else f"fraud_ip_{ring_id}_{account_index:03d}"
        )

        for _ in range(
            transactions_per_account
        ):
            transaction_index = len(output)

            transaction = Transaction(
                transaction_id=(
                    f"txn_{transaction_index:06d}"
                ),
                customer_id=customer_id,
                merchant_id=(
                    f"merchant_{rng.randint(1, 50):03d}"
                ),
                device_id=device_id,
                card_id=card_id,
                ip_id=ip_id,
                amount=round(
                    rng.uniform(
                        100.0,
                        5000.0,
                    ),
                    2,
                ),
                timestamp=(
                    start_time
                    + timedelta(
                        minutes=rng.randint(
                            1,
                            180,
                        )
                    )
                ),
                account_age_days=account_age_days,
                is_fraud=True,
                fraud_ring_id=ring_id,
            )

            output.append(
                transaction
            )

    return output


def inject_multiple_device_farms(
    transactions: list[Transaction],
    ring_count: int,
    ring_size: int = 5,
    transactions_per_account: int = 3,
    seed: int = 42,
    shared_device_ratio: float = 0.8,
    shared_ip_ratio: float = 0.7,
) -> list[Transaction]:
    if ring_count < 1:
        raise ValueError(
            "ring_count must be at least 1"
        )

    output = list(transactions)

    for ring_index in range(
        1,
        ring_count + 1,
    ):
        output = inject_device_farm(
            output,
            ring_id=(
                f"ring_{ring_index:03d}"
            ),
            ring_size=ring_size,
            transactions_per_account=(
                transactions_per_account
            ),
            seed=seed + ring_index,
            shared_device_ratio=(
                shared_device_ratio
            ),
            shared_ip_ratio=(
                shared_ip_ratio
            ),
        )

    return output