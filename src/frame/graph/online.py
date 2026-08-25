from __future__ import annotations

import networkx as nx

from frame.domain.transaction import Transaction


def _degree(
    graph: nx.Graph,
    node: str,
) -> float:
    if node not in graph:
        return 0.0

    return float(
        graph.degree(node)
    )


def _component_exposure(
    graph: nx.Graph,
    nodes: list[str],
) -> float:
    exposed_nodes: set[str] = set()

    for node in nodes:
        if node not in graph:
            continue

        exposed_nodes.update(
            nx.node_connected_component(
                graph,
                node,
            )
        )

    return float(
        len(exposed_nodes)
    )


def extract_online_graph_features(
    transaction: Transaction,
    graph: nx.Graph,
) -> dict[str, float]:
    customer_node = (
        f"customer:{transaction.customer_id}"
    )
    card_node = (
        f"card:{transaction.card_id}"
    )
    device_node = (
        f"device:{transaction.device_id}"
    )
    ip_node = (
        f"ip:{transaction.ip_id}"
    )
    merchant_node = (
        f"merchant:{transaction.merchant_id}"
    )

    referenced_nodes = [
        customer_node,
        card_node,
        device_node,
        ip_node,
        merchant_node,
    ]

    return {
        "customer_degree": _degree(
            graph,
            customer_node,
        ),
        "card_degree": _degree(
            graph,
            card_node,
        ),
        "device_degree": _degree(
            graph,
            device_node,
        ),
        "ip_degree": _degree(
            graph,
            ip_node,
        ),
        "merchant_degree": _degree(
            graph,
            merchant_node,
        ),
        "component_size": (
            _component_exposure(
                graph,
                referenced_nodes,
            )
        ),
    }