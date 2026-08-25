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

    result = evaluate_independent_worlds(
        train_world,
        test_world,
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=1000.0,
    )

    sweep = sweep_thresholds(
        result.test_labels,
        result.hybrid_probabilities,
        cost_model,
        thresholds=[
            0.50,
            0.55,
            0.60,
            0.65,
            0.70,
            0.75,
            0.80,
            0.85,
            0.90,
            0.95,
        ],
    )

    print("FRAME E04 — Threshold Sweep")
    print("=" * 72)

    print(
        f"{'Threshold':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1':<12}"
        f"{'FP':<8}"
        f"{'FN':<8}"
        f"{'Cost':<12}"
    )

    for point in sweep:
        print(
            f"{point.threshold:<12.2f}"
            f"{point.precision:<12.4f}"
            f"{point.recall:<12.4f}"
            f"{point.f1:<12.4f}"
            f"{point.false_positives:<8}"
            f"{point.false_negatives:<8}"
            f"{point.total_cost:<12.2f}"
        )

    best = min(
        sweep,
        key=lambda point: point.total_cost,
    )

    print("\nBest threshold by financial cost")
    print(f"Threshold: {best.threshold:.2f}")
    print(f"Precision: {best.precision:.4f}")
    print(f"Recall:    {best.recall:.4f}")
    print(f"F1:        {best.f1:.4f}")
    print(f"Cost:      {best.total_cost:.2f}")


if __name__ == "__main__":
    main()