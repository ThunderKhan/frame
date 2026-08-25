from frame.evaluation.hard_negatives import (
    evaluate_hard_negatives,
)
from frame.evaluation.independent import (
    evaluate_independent_worlds,
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

    hard_negative_metrics = evaluate_hard_negatives(
        test_world.transactions,
        result.hybrid_probabilities,
        threshold=0.5,
    )

    print("FRAME E02 — Benign False Positives")
    print("=" * 45)

    print("\nShared-IP benign traffic")
    print(
        f"Transactions: "
        f"{hard_negative_metrics.shared_ip_count}"
    )
    print(
        f"Flagged:      "
        f"{hard_negative_metrics.shared_ip_flagged}"
    )
    print(
        "False-positive rate: "
        f"{hard_negative_metrics.shared_ip_false_positive_rate:.4f}"
    )

    print("\nShared-device benign traffic")
    print(
        f"Transactions: "
        f"{hard_negative_metrics.shared_device_count}"
    )
    print(
        f"Flagged:      "
        f"{hard_negative_metrics.shared_device_flagged}"
    )
    print(
        "False-positive rate: "
        f"{hard_negative_metrics.shared_device_false_positive_rate:.4f}"
    )


if __name__ == "__main__":
    main()