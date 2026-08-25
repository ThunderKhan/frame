from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from frame.domain.transaction import Transaction


def build_temporal_features(
    transactions: list[Transaction],
    window_minutes: int = 30,
) -> dict[str, dict[str, float]]:
    sorted_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.timestamp,
    )

    by_device: dict[str, list[Transaction]] = defaultdict(list)
    by_ip: dict[str, list[Transaction]] = defaultdict(list)
    by_customer: dict[str, list[Transaction]] = defaultdict(list)

    for transaction in sorted_transactions:
        by_device[transaction.device_id].append(transaction)
        by_ip[transaction.ip_id].append(transaction)
        by_customer[transaction.customer_id].append(transaction)

    window = timedelta(minutes=window_minutes)

    features: dict[str, dict[str, float]] = {}

    for transaction in sorted_transactions:
        start_time = transaction.timestamp - window

        recent_device_transactions = [
            candidate
            for candidate in by_device[transaction.device_id]
            if start_time
            <= candidate.timestamp
            <= transaction.timestamp
        ]

        recent_ip_transactions = [
            candidate
            for candidate in by_ip[transaction.ip_id]
            if start_time
            <= candidate.timestamp
            <= transaction.timestamp
        ]

        recent_customer_transactions = [
            candidate
            for candidate in by_customer[transaction.customer_id]
            if start_time
            <= candidate.timestamp
            <= transaction.timestamp
        ]

        recent_device_customers = {
            candidate.customer_id
            for candidate in recent_device_transactions
        }

        recent_ip_customers = {
            candidate.customer_id
            for candidate in recent_ip_transactions
        }

        recent_merchants = {
            candidate.merchant_id
            for candidate in recent_device_transactions
        }

        features[transaction.transaction_id] = {
            "device_transactions_30m": float(
                len(recent_device_transactions)
            ),
            "ip_transactions_30m": float(
                len(recent_ip_transactions)
            ),
            "customer_transactions_30m": float(
                len(recent_customer_transactions)
            ),
            "device_customers_30m": float(
                len(recent_device_customers)
            ),
            "ip_customers_30m": float(
                len(recent_ip_customers)
            ),
            "device_merchants_30m": float(
                len(recent_merchants)
            ),
        }

    return features