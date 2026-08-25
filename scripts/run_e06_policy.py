from frame.evaluation.independent import (
    evaluate_independent_worlds,
)
from frame.evaluation.policy import (
    evaluate_policy,
)
from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)
from frame.risk.policy import RiskPolicy


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

    policy = RiskPolicy(
        review_threshold=0.80,
        block_threshold=0.95,
    )

    metrics = evaluate_policy(
        result.test_labels,
        result.hybrid_probabilities,
        policy,
    )

    print("FRAME E06 — Risk Policy")
    print("=" * 45)

    print(f"\nAllowed:  {metrics.allowed}")
    print(f"Reviewed: {metrics.reviewed}")
    print(f"Blocked:  {metrics.blocked}")

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


if __name__ == "__main__":
    main()