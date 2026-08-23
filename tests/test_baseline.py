from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions
from frame.risk.baseline import (
    build_labels,
    build_transaction_feature_matrix,
    train_transaction_baseline,
)


def build_training_dataset():
    legitimate = generate_legitimate_transactions(
        count=500,
        seed=42,
    )

    return inject_device_farm(
        legitimate,
        ring_id="ring_train",
        ring_size=10,
        transactions_per_account=5,
        seed=42,
    )


def test_transaction_feature_matrix_shape() -> None:
    transactions = build_training_dataset()

    matrix = build_transaction_feature_matrix(
        transactions,
    )

    assert matrix.shape == (
        len(transactions),
        2,
    )


def test_labels_match_dataset_size() -> None:
    transactions = build_training_dataset()

    labels = build_labels(transactions)

    assert len(labels) == len(transactions)
    assert set(labels) == {0, 1}


def test_transaction_baseline_can_train() -> None:
    transactions = build_training_dataset()

    model = train_transaction_baseline(
        transactions,
    )

    matrix = build_transaction_feature_matrix(
        transactions,
    )

    predictions = model.predict(matrix)

    assert len(predictions) == len(transactions)