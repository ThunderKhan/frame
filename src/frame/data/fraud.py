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
) -> list[Transaction]:
    if not transactions:
        raise ValueError("transactions must not be empty")

    if ring_size < 2:
        raise ValueError("ring_size must be at least 2")

    if transactions_per_account < 1:
        raise ValueError("transactions_per_account must be at least 1")

    rng = Random(seed)

    output = list(transactions)

    start_time = max(transaction.timestamp for transaction in transactions)

    shared_device_id = f"fraud_device_{ring_id}"
    shared_ip_id = f"fraud_ip_{ring_id}"

    for account_index in range(1, ring_size + 1):
        customer_id = f"fraud_customer_{ring_id}_{account_index:03d}"
        card_id = f"fraud_card_{ring_id}_{account_index:03d}"

        account_age_days = rng.randint(0, 7)

        for local_transaction_index in range(transactions_per_account):
            transaction_index = len(output)

            transaction = Transaction(
                transaction_id=f"txn_{transaction_index:06d}",
                customer_id=customer_id,
                merchant_id=f"merchant_{rng.randint(1, 5):03d}",
                device_id=shared_device_id,
                card_id=card_id,
                ip_id=shared_ip_id,
                amount=round(rng.uniform(500.0, 1800.0), 2),
                timestamp=start_time
                + timedelta(
                    minutes=rng.randint(1, 30),
                ),
                account_age_days=account_age_days,
                is_fraud=True,
                fraud_ring_id=ring_id,
            )

            output.append(transaction)

    return output