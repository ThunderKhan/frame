from frame.evaluation.cost import (
    CostModel,
)
from frame.evaluation.latency import (
    evaluate_ring_detection_latency,
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

    best = min(
        sweep,
        key=lambda point: point.total_cost,
    )

    locked_threshold = best.threshold

    test_features = (
        build_online_feature_matrix(
            test_world.transactions
        )
    )

    test_probabilities = (
        model.predict_proba(
            test_features
        )[:, 1]
    )

    latency_results = (
        evaluate_ring_detection_latency(
            test_world.transactions,
            test_probabilities,
            threshold=locked_threshold,
        )
    )

    print("FRAME E05c — Fraud Ring Detection Latency")
    print("=" * 60)

    print(
        f"\nLocked threshold: "
        f"{locked_threshold:.3f}"
    )

    detected_count = 0

    for result in latency_results:
        print(
            f"\n{result.ring_id}"
        )

        print(
            "Fraud transactions: "
            f"{result.fraud_transactions}"
        )

        if (
            result.transactions_until_detection
            is None
        ):
            print("Detection: NOT DETECTED")
            continue

        detected_count += 1

        print(
            "Transactions until first detection: "
            f"{result.transactions_until_detection}"
        )

        print(
            "Time until first detection: "
            f"{result.time_until_detection}"
        )

    print("\nSummary")
    print("=" * 30)

    print(
        "Rings detected: "
        f"{detected_count}/"
        f"{len(latency_results)}"
    )

    detected = [
        result
        for result in latency_results
        if result.transactions_until_detection
        is not None
    ]

    if detected:
        average_transactions = (
            sum(
                result.transactions_until_detection
                for result in detected
                if result.transactions_until_detection
                is not None
            )
            / len(detected)
        )

        print(
            "Average fraud transactions "
            "before detection: "
            f"{average_transactions:.2f}"
        )


if __name__ == "__main__":
    main()