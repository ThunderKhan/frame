from datetime import (
    UTC,
    datetime,
    timedelta,
)

from frame.domain.transaction import (
    Transaction,
)
from frame.graph.temporal import (
    build_temporal_features,
)
from frame.graph.temporal_online import (
    OnlineTemporalState,
)


def make_transaction(
    index: int,
    minute: int,
    customer_id: str,
    device_id: str,
    ip_id: str,
    merchant_id: str,
) -> Transaction:
    return Transaction(
        transaction_id=f"txn_{index:03d}",
        customer_id=customer_id,
        merchant_id=merchant_id,
        device_id=device_id,
        card_id=f"card_{index:03d}",
        ip_id=ip_id,
        amount=500.0,
        timestamp=(
            datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            )
            + timedelta(minutes=minute)
        ),
        account_age_days=200,
    )


def test_online_temporal_matches_batch_temporal_prefixes() -> None:
    transactions = [
        make_transaction(
            1,
            0,
            "cust_001",
            "device_shared",
            "ip_shared",
            "merchant_001",
        ),
        make_transaction(
            2,
            5,
            "cust_002",
            "device_shared",
            "ip_shared",
            "merchant_002",
        ),
        make_transaction(
            3,
            20,
            "cust_001",
            "device_shared",
            "ip_shared",
            "merchant_003",
        ),
        make_transaction(
            4,
            45,
            "cust_003",
            "device_shared",
            "ip_shared",
            "merchant_001",
        ),
    ]

    state = OnlineTemporalState(
        window_minutes=30
    )

    history: list[Transaction] = []

    for transaction in transactions:
        online = (
            state.extract_and_update(
                transaction
            )
        )

        history.append(transaction)

        expected = build_temporal_features(
            history,
            window_minutes=30,
        )[transaction.transaction_id]

        assert online == expected