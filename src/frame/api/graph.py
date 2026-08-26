from __future__ import annotations

import networkx as nx


def serialize_graph(
    graph: nx.Graph,
) -> dict[str, list[dict[str, object]]]:
    nodes: list[dict[str, object]] = []

    for node_id, attributes in graph.nodes(
        data=True
    ):
        nodes.append(
            {
                "id": node_id,
                "attributes": dict(
                    attributes
                ),
            }
        )

    edges: list[dict[str, object]] = []

    for source, target, attributes in graph.edges(
        data=True
    ):
        edges.append(
            {
                "source": source,
                "target": target,
                "attributes": dict(
                    attributes
                ),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
    }