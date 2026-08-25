from __future__ import annotations

from collections import defaultdict, deque
from datetime import timedelta

from frame.domain.transaction import Transaction


class OnlineTemporalState:
    def __init__(
        self,
        window_minutes: int = 30,
    ) -> None:
        if window_minutes <= 0:
            raise ValueError(
                "window_minutes must be positive"
            )

        self.window = timedelta(
            minutes=window_minutes
        )

        self.by_device: dict[
            str,
            deque[Transaction],
        ] = defaultdict(deque)

        self.by_ip: dict[
            str,
            deque[Transaction],
        ] = defaultdict(deque)

        self.by_customer: dict[
            str,
            deque[Transaction],
        ] = defaultdict(deque)

    def _purge(
        self,
        events: deque[Transaction],
        current: Transaction,
    ) -> None:
        cutoff = (
            current.timestamp
            - self.window
        )

        while (
            events
            and events[0].timestamp
            < cutoff
        ):
            events.popleft()

    def extract_and_update(
        self,
        transaction: Transaction,
    ) -> dict[str, float]:
        device_events = self.by_device[
            transaction.device_id
        ]

        ip_events = self.by_ip[
            transaction.ip_id
        ]

        customer_events = self.by_customer[
            transaction.customer_id
        ]

        self._purge(
            device_events,
            transaction,
        )
        self._purge(
            ip_events,
            transaction,
        )
        self._purge(
            customer_events,
            transaction,
        )

        device_customers = {
            event.customer_id
            for event in device_events
        }
        device_customers.add(
            transaction.customer_id
        )

        ip_customers = {
            event.customer_id
            for event in ip_events
        }
        ip_customers.add(
            transaction.customer_id
        )

        device_merchants = {
            event.merchant_id
            for event in device_events
        }
        device_merchants.add(
            transaction.merchant_id
        )

        features = {
            "device_transactions_30m": float(
                len(device_events) + 1
            ),
            "ip_transactions_30m": float(
                len(ip_events) + 1
            ),
            "customer_transactions_30m": float(
                len(customer_events) + 1
            ),
            "device_customers_30m": float(
                len(device_customers)
            ),
            "ip_customers_30m": float(
                len(ip_customers)
            ),
            "device_merchants_30m": float(
                len(device_merchants)
            ),
        }

        device_events.append(transaction)
        ip_events.append(transaction)
        customer_events.append(transaction)

        return features