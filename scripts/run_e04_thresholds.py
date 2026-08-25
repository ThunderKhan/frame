from frame.evaluation.cost import CostModel
from frame.evaluation.independent import (
    evaluate_independent_worlds,
)
from frame.evaluation.sweep import (
    sweep_thresholds,
)
from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)


def main() -> None:
    train_world = build_synthetic_world(
        legitimate_count=10_000,
        ring_count=5,
        ring_size=8,
        transactions_per_account=4,
        seed=42,
    )

    validation_world = build_hard_negative_world(
        legitimate_count=5_000,
        ring_count=3,
        ring_size=8,
        transactions_per_account=4,
        seed=7331,
        shared_ip_group_count=10,
        shared_ip_customers_per_group=8,
        shared_device_group_count=8,
        shared_device_customers_per_group=3,
    )

    test_world = build_hard_negative_world(
        legitimate_count=5_000,
        ring_count=3,
        ring_size=8,
        transactions_per_account=4,
        seed=1337,
        shared_ip_group_count=10,
        shared_ip_customers_per_group=8,
        shared_device_group_count=8,
        shared_device_customers_per_group=3,
    )

    validation_result = evaluate_independent_worlds(
        train_world,
        validation_world,
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=1000.0,
    )

    thresholds = [
        0.50,
        0.60,
        0.70,
        0.80,
        0.85,
        0.90,
        0.92,
        0.94,
        0.95,
        0.96,
        0.97,
        0.98,
        0.985,
        0.99,
        0.995,
        0.999,
    ]

    validation_sweep = sweep_thresholds(
        validation_result.test_labels,
        validation_result.hybrid_probabilities,
        cost_model,
        thresholds=thresholds,
    )

    print("FRAME E04 — VALIDATION THRESHOLD SWEEP")
    print("=" * 78)

    print(
        f"{'Threshold':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1':<12}"
        f"{'FP':<8}"
        f"{'FN':<8}"
        f"{'Cost':<12}"
    )

    for point in validation_sweep:
        print(
            f"{point.threshold:<12.3f}"
            f"{point.precision:<12.4f}"
            f"{point.recall:<12.4f}"
            f"{point.f1:<12.4f}"
            f"{point.false_positives:<8}"
            f"{point.false_negatives:<8}"
            f"{point.total_cost:<12.2f}"
        )

    best = min(
        validation_sweep,
        key=lambda point: point.total_cost,
    )

    locked_threshold = best.threshold

    print("\nSelected on validation set")
    print(f"Threshold: {locked_threshold:.3f}")

    test_result = evaluate_independent_worlds(
        train_world,
        test_world,
    )

    test_point = sweep_thresholds(
        test_result.test_labels,
        test_result.hybrid_probabilities,
        cost_model,
        thresholds=[locked_threshold],
    )[0]

    print("\nLOCKED THRESHOLD — FINAL TEST")
    print("=" * 45)

    print(f"Threshold: {test_point.threshold:.3f}")
    print(f"Precision: {test_point.precision:.4f}")
    print(f"Recall:    {test_point.recall:.4f}")
    print(f"F1:        {test_point.f1:.4f}")
    print(f"FP:        {test_point.false_positives}")
    print(f"FN:        {test_point.false_negatives}")
    print(f"Cost:      {test_point.total_cost:.2f}")


if __name__ == "__main__":
    main()