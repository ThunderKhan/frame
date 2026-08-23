from __future__ import annotations

import networkx as nx

from frame.domain.transaction import Transaction


def build_payment_graph(
    transactions: list[Transaction],
) -> nx.Graph:
    graph = nx.Graph()

    for transaction in transactions:
        customer_node = f"customer:{transaction.customer_id}"
        card_node = f"card:{transaction.card_id}"
        device_node = f"device:{transaction.device_id}"
        ip_node = f"ip:{transaction.ip_id}"
        merchant_node = f"merchant:{transaction.merchant_id}"

        graph.add_node(
            customer_node,
            node_type="customer",
            entity_id=transaction.customer_id,
        )
        graph.add_node(
            card_node,
            node_type="card",
            entity_id=transaction.card_id,
        )
        graph.add_node(
            device_node,
            node_type="device",
            entity_id=transaction.device_id,
        )
        graph.add_node(
            ip_node,
            node_type="ip",
            entity_id=transaction.ip_id,
        )
        graph.add_node(
            merchant_node,
            node_type="merchant",
            entity_id=transaction.merchant_id,
        )

        graph.add_edge(
            customer_node,
            card_node,
            relation="uses_card",
        )

        graph.add_edge(
            customer_node,
            device_node,
            relation="uses_device",
        )

        graph.add_edge(
            customer_node,
            ip_node,
            relation="uses_ip",
        )

        graph.add_edge(
            customer_node,
            merchant_node,
            relation="transacts_with",
        )

    return graph