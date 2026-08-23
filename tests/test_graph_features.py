from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions
from frame.graph.builder import build_payment_graph
from frame.graph.features import extract_graph_features


def test_graph_features_are_extracted() -> None:
    transactions = generate_legitimate_transactions(
        count=50,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    features = extract_graph_features(
        transactions[0],
        graph,
    )

    assert set(features) == {
        "customer_degree",
        "card_degree",
        "device_degree",
        "ip_degree",
        "merchant_degree",
        "component_size",
    }


def test_shared_fraud_device_has_high_degree() -> None:
    legitimate = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    transactions = inject_device_farm(
        legitimate,
        ring_id="ring_features",
        ring_size=6,
        transactions_per_account=2,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    fraud_transaction = next(
        transaction
        for transaction in transactions
        if transaction.fraud_ring_id == "ring_features"
    )

    features = extract_graph_features(
        fraud_transaction,
        graph,
    )

    assert features["device_degree"] == 6.0
    assert features["ip_degree"] == 6.0


def test_fraud_component_is_larger_than_single_customer_structure() -> None:
    legitimate = generate_legitimate_transactions(
        count=100,
        seed=42,
    )

    transactions = inject_device_farm(
        legitimate,
        ring_id="ring_component",
        ring_size=5,
        transactions_per_account=2,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    fraud_transaction = next(
        transaction
        for transaction in transactions
        if transaction.fraud_ring_id == "ring_component"
    )

    features = extract_graph_features(
        fraud_transaction,
        graph,
    )

    assert features["component_size"] > 5