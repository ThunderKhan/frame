from __future__ import annotations

from datetime import UTC, datetime, timedelta
from random import Random

from frame.domain.customer import CustomerProfile
from frame.domain.transaction import Transaction


def generate_customer_profiles(
    count: int,
    seed: int = 42,
) -> list[CustomerProfile]:
    rng = Random(seed)

    customers: list[CustomerProfile] = []

    card_counter = 1
    device_counter = 1
    ip_counter = 1

    for customer_index in range(1, count + 1):
        num_cards = rng.randint(1, 3)
        num_devices = rng.randint(1, 2)
        num_ips = rng.randint(1, 3)

        card_ids = [
            f"card_{card_counter + offset:05d}"
            for offset in range(num_cards)
        ]
        card_counter += num_cards

        device_ids = [
            f"device_{device_counter + offset:05d}"
            for offset in range(num_devices)
        ]
        device_counter += num_devices

        ip_ids = [
            f"ip_{ip_counter + offset:05d}"
            for offset in range(num_ips)
        ]
        ip_counter += num_ips

        customer = CustomerProfile(
            customer_id=f"cust_{customer_index:05d}",
            card_ids=card_ids,
            device_ids=device_ids,
            ip_ids=ip_ids,
            account_age_days=rng.randint(30, 1500),
        )

        customers.append(customer)

    return customers


def generate_legitimate_transactions(
    count: int,
    customer_count: int = 500,
    merchant_count: int = 50,
    seed: int = 42,
    start_time: datetime | None = None,
) -> list[Transaction]:
    rng = Random(seed)

    base_time = start_time or datetime(2026, 1, 1, tzinfo=UTC)

    customers = generate_customer_profiles(
        count=customer_count,
        seed=seed,
    )

    transactions: list[Transaction] = []

    for transaction_index in range(count):
        customer = rng.choice(customers)

        transaction = Transaction(
            transaction_id=f"txn_{transaction_index:06d}",
            customer_id=customer.customer_id,
            merchant_id=f"merchant_{rng.randint(1, merchant_count):03d}",
            device_id=rng.choice(customer.device_ids),
            card_id=rng.choice(customer.card_ids),
            ip_id=rng.choice(customer.ip_ids),
            amount=round(rng.uniform(100.0, 5000.0), 2),
            timestamp=base_time
            + timedelta(
                seconds=rng.randint(0, 7 * 24 * 3600),
            ),
            account_age_days=customer.account_age_days,
        )

        transactions.append(transaction)

    return transactions