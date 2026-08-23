from __future__ import annotations

import networkx as nx

from frame.domain.transaction import Transaction


def extract_graph_features(
    transaction: Transaction,
    graph: nx.Graph,
) -> dict[str, float]:
    customer_node = f"customer:{transaction.customer_id}"
    card_node = f"card:{transaction.card_id}"
    device_node = f"device:{transaction.device_id}"
    ip_node = f"ip:{transaction.ip_id}"
    merchant_node = f"merchant:{transaction.merchant_id}"

    device_degree = graph.degree(device_node)
    ip_degree = graph.degree(ip_node)
    card_degree = graph.degree(card_node)
    merchant_degree = graph.degree(merchant_node)
    customer_degree = graph.degree(customer_node)

    component = nx.node_connected_component(
        graph,
        customer_node,
    )

    component_size = len(component)

    return {
        "customer_degree": float(customer_degree),
        "card_degree": float(card_degree),
        "device_degree": float(device_degree),
        "ip_degree": float(ip_degree),
        "merchant_degree": float(merchant_degree),
        "component_size": float(component_size),
    }


def extract_dataset_graph_features(
    transactions: list[Transaction],
    graph: nx.Graph,
) -> list[dict[str, float]]:
    return [
        extract_graph_features(
            transaction,
            graph,
        )
        for transaction in transactions
    ]