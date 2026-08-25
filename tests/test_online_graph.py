from datetime import UTC, datetime

import networkx as nx

from frame.domain.transaction import Transaction
from frame.graph.builder import (
    add_transaction_to_graph,
)
from frame.graph.online import (
    extract_online_graph_features,
)


def make_transaction(
    transaction_id: str,
    customer_id: str,
    device_id: str,
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        customer_id=customer_id,
        merchant_id="merchant_001",
        device_id=device_id,
        card_id=f"card_{customer_id}",
        ip_id="ip_001",
        amount=500.0,
        timestamp=datetime.now(UTC),
        account_age_days=200,
    )


def test_online_features_only_see_existing_graph() -> None:
    graph = nx.Graph()

    first = make_transaction(
        "txn_001",
        "cust_001",
        "device_shared",
    )

    second = make_transaction(
        "txn_002",
        "cust_002",
        "device_shared",
    )

    before = extract_online_graph_features(
        first,
        graph,
    )

    assert before["device_degree"] == 0.0

    add_transaction_to_graph(
        graph,
        first,
    )

    after = extract_online_graph_features(
        second,
        graph,
    )

    assert after["device_degree"] == 1.0