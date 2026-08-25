from frame.evaluation.cost import CostModel
from frame.evaluation.metrics import (
    evaluate_predictions,
)
from frame.evaluation.sweep import (
    sweep_thresholds,
)
from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)
from frame.risk.baseline import (
    build_labels,
)
from frame.risk.online import (
    build_online_feature_matrix,
    train_online_hybrid_model,
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

    model = train_online_hybrid_model(
        train_world.transactions
    )

    validation_features = (
        build_online_feature_matrix(
            validation_world.transactions
        )
    )

    validation_labels = build_labels(
        validation_world.transactions
    )

    validation_probabilities = (
        model.predict_proba(
            validation_features
        )[:, 1]
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=1000.0,
    )

    thresholds = [
        0.02,
        0.05,
        0.08,
        0.10,
        0.12,
        0.15,
        0.18,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
    ]

    sweep = sweep_thresholds(
        validation_labels,
        validation_probabilities,
        cost_model,
        thresholds=thresholds,
    )

    print("FRAME E05b — Online Threshold Selection")
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

    for point in sweep:
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
        sweep,
        key=lambda point: point.total_cost,
    )

    locked_threshold = best.threshold

    print("\nSelected on validation")
    print(
        f"Threshold: {locked_threshold:.3f}"
    )

    test_features = (
        build_online_feature_matrix(
            test_world.transactions
        )
    )

    test_labels = build_labels(
        test_world.transactions
    )

    test_probabilities = (
        model.predict_proba(
            test_features
        )[:, 1]
    )

    test_predictions = (
        test_probabilities
        >= locked_threshold
    ).astype(int)

    test_metrics = evaluate_predictions(
        test_labels,
        test_predictions,
        test_probabilities,
    )

    test_point = sweep_thresholds(
        test_labels,
        test_probabilities,
        cost_model,
        thresholds=[locked_threshold],
    )[0]

    print("\nLOCKED THRESHOLD — FINAL TEST")
    print("=" * 45)

    print(
        f"Threshold: {locked_threshold:.3f}"
    )
    print(
        f"Precision: {test_metrics.precision:.4f}"
    )
    print(
        f"Recall:    {test_metrics.recall:.4f}"
    )
    print(
        f"F1:        {test_metrics.f1:.4f}"
    )
    print(
        f"PR-AUC:    {test_metrics.pr_auc:.4f}"
    )
    print(
        f"FP:        {test_point.false_positives}"
    )
    print(
        f"FN:        {test_point.false_negatives}"
    )


if __name__ == "__main__":
    main()