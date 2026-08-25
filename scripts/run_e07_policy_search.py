from frame.evaluation.independent import (
    evaluate_independent_worlds,
)
from frame.evaluation.policy import (
    evaluate_policy,
)
from frame.evaluation.policy_search import (
    PolicyCostModel,
    search_policy_thresholds,
)
from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)


def print_policy_metrics(
    title: str,
    metrics,
) -> None:
    print(f"\n{title}")
    print("=" * 50)

    print(f"Allowed:  {metrics.allowed}")
    print(f"Reviewed: {metrics.reviewed}")
    print(f"Blocked:  {metrics.blocked}")

    print("\nFraud")
    print(f"Allowed:  {metrics.fraud_allowed}")
    print(f"Reviewed: {metrics.fraud_reviewed}")
    print(f"Blocked:  {metrics.fraud_blocked}")

    print("\nLegitimate")
    print(
        f"Allowed:  "
        f"{metrics.legitimate_allowed}"
    )
    print(
        f"Reviewed: "
        f"{metrics.legitimate_reviewed}"
    )
    print(
        f"Blocked:  "
        f"{metrics.legitimate_blocked}"
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

    cost_model = PolicyCostModel(
        legitimate_review_cost=10.0,
        legitimate_block_cost=500.0,
        fraud_allow_cost=1000.0,
        fraud_review_cost=50.0,
    )

    review_thresholds = [
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
    ]

    block_thresholds = [
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.92,
        0.94,
        0.95,
        0.97,
        0.99,
    ]

    results = search_policy_thresholds(
        validation_result.test_labels,
        validation_result.hybrid_probabilities,
        cost_model,
        review_thresholds,
        block_thresholds,
    )

    best = min(
        results,
        key=lambda result: result.total_cost,
    )

    print("FRAME E07 — Policy Search")
    print("=" * 50)

    print("\nSelected on validation world")
    print(
        "Review threshold: "
        f"{best.policy.review_threshold:.3f}"
    )
    print(
        "Block threshold:  "
        f"{best.policy.block_threshold:.3f}"
    )
    print(
        f"Validation cost: "
        f"{best.total_cost:.2f}"
    )

    print_policy_metrics(
        "Validation metrics",
        best.metrics,
    )

    test_result = evaluate_independent_worlds(
        train_world,
        test_world,
    )

    test_metrics = evaluate_policy(
        test_result.test_labels,
        test_result.hybrid_probabilities,
        best.policy,
    )

    print_policy_metrics(
        "Locked policy — final test",
        test_metrics,
    )


if __name__ == "__main__":
    main()