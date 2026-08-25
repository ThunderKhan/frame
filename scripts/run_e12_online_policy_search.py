from __future__ import annotations

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
from frame.risk.baseline import (
    build_labels,
)
from frame.risk.online import (
    build_online_feature_matrix,
    train_online_hybrid_model,
)


def print_metrics(
    title: str,
    metrics,
) -> None:
    print(f"\n{title}")
    print("=" * 52)

    print(
        f"Allowed:  {metrics.allowed}"
    )
    print(
        f"Reviewed: {metrics.reviewed}"
    )
    print(
        f"Blocked:  {metrics.blocked}"
    )

    print("\nFraud")
    print(
        f"Allowed:  {metrics.fraud_allowed}"
    )
    print(
        f"Reviewed: {metrics.fraud_reviewed}"
    )
    print(
        f"Blocked:  {metrics.fraud_blocked}"
    )

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

    cost_model = PolicyCostModel(
        legitimate_review_cost=10.0,
        legitimate_block_cost=500.0,
        fraud_allow_cost=1000.0,
        fraud_review_cost=50.0,
    )

    review_thresholds = [
        0.02,
        0.03,
        0.04,
        0.05,
        0.06,
        0.08,
        0.10,
        0.12,
        0.15,
        0.18,
        0.20,
    ]

    block_thresholds = [
        0.15,
        0.18,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
    ]

    results = search_policy_thresholds(
        validation_labels,
        validation_probabilities,
        cost_model,
        review_thresholds,
        block_thresholds,
    )

    best = min(
        results,
        key=lambda result: result.total_cost,
    )

    print(
        "FRAME E12 — Online Policy Search"
    )
    print("=" * 52)

    print(
        "\nSelected on validation"
    )

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

    print_metrics(
        "Validation metrics",
        best.metrics,
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

    test_metrics = evaluate_policy(
        test_labels,
        test_probabilities,
        best.policy,
    )

    print_metrics(
        "LOCKED POLICY — FINAL TEST",
        test_metrics,
    )


if __name__ == "__main__":
    main()