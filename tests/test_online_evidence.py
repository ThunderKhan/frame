from datetime import UTC, datetime

from frame.domain.transaction import (
    Transaction,
)
from frame.risk.online import (
    build_online_graph_evidence_mask,
)


def make_transaction(
    transaction_id: str,
    customer_id: str,
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        customer_id=customer_id,
        merchant_id="merchant_001",
        device_id="device_shared",
        card_id=f"card_{customer_id}",
        ip_id="ip_shared",
        amount=500.0,
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        account_age_days=200,
    )


def test_cross_customer_evidence_emerges_after_first_customer() -> None:
    transactions = [
        make_transaction(
            "txn_001",
            "cust_001",
        ),
        make_transaction(
            "txn_002",
            "cust_002",
        ),
    ]

    evidence = (
        build_online_graph_evidence_mask(
            transactions
        )
    )

    assert not bool(evidence[0])
    assert bool(evidence[1])