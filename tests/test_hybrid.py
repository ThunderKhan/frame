from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions
from frame.graph.builder import build_payment_graph
from frame.risk.hybrid import (
    build_hybrid_feature_matrix,
    train_hybrid_model,
)


def build_dataset():
    legitimate = generate_legitimate_transactions(
        count=500,
        seed=42,
    )

    transactions = inject_device_farm(
        legitimate,
        ring_id="ring_hybrid",
        ring_size=10,
        transactions_per_account=5,
        seed=42,
    )

    graph = build_payment_graph(transactions)

    return transactions, graph


def test_hybrid_feature_matrix_shape() -> None:
    transactions, graph = build_dataset()

    matrix = build_hybrid_feature_matrix(
        transactions,
        graph,
    )

    assert matrix.shape == (
        len(transactions),
        14,
    )


def test_hybrid_model_can_train() -> None:
    transactions, graph = build_dataset()

    model = train_hybrid_model(
        transactions,
        graph,
    )

    matrix = build_hybrid_feature_matrix(
        transactions,
        graph,
    )

    predictions = model.predict(matrix)

    assert len(predictions) == len(transactions)