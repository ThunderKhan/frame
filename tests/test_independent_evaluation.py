from frame.evaluation.independent import (
    evaluate_independent_worlds,
)
from frame.evaluation.worlds import (
    build_synthetic_world,
)


def test_independent_world_evaluation_runs() -> None:
    train_world = build_synthetic_world(
        legitimate_count=500,
        ring_count=3,
        ring_size=5,
        transactions_per_account=3,
        seed=42,
    )

    test_world = build_synthetic_world(
        legitimate_count=250,
        ring_count=2,
        ring_size=5,
        transactions_per_account=3,
        seed=99,
    )

    result = (
        evaluate_independent_worlds(
            train_world,
            test_world,
        )
    )

    for metrics in (
        result.baseline,
        result.hybrid,
    ):
        assert 0.0 <= metrics.precision <= 1.0
        assert 0.0 <= metrics.recall <= 1.0
        assert 0.0 <= metrics.f1 <= 1.0
        assert 0.0 <= metrics.pr_auc <= 1.0


def test_train_and_test_worlds_use_different_seeds() -> None:
    train_world = build_synthetic_world(
        legitimate_count=100,
        ring_count=1,
        ring_size=4,
        transactions_per_account=2,
        seed=42,
    )

    test_world = build_synthetic_world(
        legitimate_count=100,
        ring_count=1,
        ring_size=4,
        transactions_per_account=2,
        seed=99,
    )

    assert (
        train_world.seed
        != test_world.seed
    )