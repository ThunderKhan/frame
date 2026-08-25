from frame.data.fraud import inject_device_farm
from frame.data.generator import generate_legitimate_transactions
from frame.evaluation.experiment import compare_models


def build_evaluation_dataset():
    legitimate = generate_legitimate_transactions(
        count=1000,
        seed=42,
    )

    return inject_device_farm(
        legitimate,
        ring_id="ring_eval",
        ring_size=20,
        transactions_per_account=5,
        seed=42,
    )


def test_model_comparison_returns_valid_metrics() -> None:
    transactions = build_evaluation_dataset()

    result = compare_models(
        transactions,
    )

    for metrics in (
        result.baseline,
        result.hybrid,
    ):
        assert 0.0 <= metrics.precision <= 1.0
        assert 0.0 <= metrics.recall <= 1.0
        assert 0.0 <= metrics.f1 <= 1.0
        assert 0.0 <= metrics.pr_auc <= 1.0