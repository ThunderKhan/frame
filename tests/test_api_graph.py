import networkx as nx

from frame.api.graph import (
    serialize_graph,
)


def test_serialize_graph() -> None:
    graph = nx.Graph()

    graph.add_node(
        "customer:1",
        type="customer",
    )

    graph.add_node(
        "device:1",
        type="device",
    )

    graph.add_edge(
        "customer:1",
        "device:1",
        relation="uses_device",
    )

    result = serialize_graph(
        graph
    )

    assert len(
        result["nodes"]
    ) == 2

    assert len(
        result["edges"]
    ) == 1

    assert result[
        "edges"
    ][0]["source"] == "customer:1"