from __future__ import annotations

from datetime import UTC, datetime, timedelta
from random import Random

from frame.domain.transaction import Transaction


def generate_legitimate_transactions(
    count: int,
    seed: int = 42,
    start_time: datetime | None = None,
) -> list[Transaction]:
    rng = Random(seed)

    base_time = start_time or datetime(2026, 1, 1, tzinfo=UTC)

    transactions: list[Transaction] = []

    for index in range(count):
        customer_num = rng.randint(1, 500)
        merchant_num = rng.randint(1, 50)

        transaction = Transaction(
            transaction_id=f"txn_{index:06d}",
            customer_id=f"cust_{customer_num:04d}",
            merchant_id=f"merchant_{merchant_num:03d}",
            device_id=f"device_{rng.randint(1, 350):04d}",
            card_id=f"card_{rng.randint(1, 700):04d}",
            ip_id=f"ip_{rng.randint(1, 250):04d}",
            amount=round(rng.uniform(100.0, 5000.0), 2),
            timestamp=base_time + timedelta(
                seconds=rng.randint(0, 7 * 24 * 3600)
            ),
            account_age_days=rng.randint(30, 1500),
        )

        transactions.append(transaction)

    return transactions