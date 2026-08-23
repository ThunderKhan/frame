from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions
from frame.graph.builder import build_payment_graph


def test_graph_contains_expected_node_types() -> None:
    transactions = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    node_types = {
        data["node_type"]
        for _, data in graph.nodes(data=True)
    }

    assert node_types == {
        "customer",
        "card",
        "device",
        "ip",
        "merchant",
    }


def test_graph_contains_customer_device_relationships() -> None:
    transactions = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    first = transactions[0]

    customer_node = f"customer:{first.customer_id}"
    device_node = f"device:{first.device_id}"

    assert graph.has_edge(
        customer_node,
        device_node,
    )

    assert (
        graph.edges[
            customer_node,
            device_node,
        ]["relation"]
        == "uses_device"
    )


def test_fraud_ring_produces_shared_device_node() -> None:
    legitimate = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    transactions = inject_device_farm(
        legitimate,
        ring_id="ring_graph",
        ring_size=5,
        transactions_per_account=2,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    shared_device = "device:fraud_device_ring_graph"

    fraud_customers = [
        node
        for node, data in graph.nodes(data=True)
        if data["node_type"] == "customer"
        and node.startswith("customer:fraud_customer_ring_graph")
    ]

    assert graph.degree(shared_device) == 5

    for customer_node in fraud_customers:
        assert graph.has_edge(
            customer_node,
            shared_device,
        )