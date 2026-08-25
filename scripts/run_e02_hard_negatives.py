from frame.evaluation.independent import (
    evaluate_independent_worlds,
)
from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)


def print_metrics(
    name: str,
    metrics,
) -> None:
    print(f"\n{name}")
    print(
        f"Precision: {metrics.precision:.4f}"
    )
    print(
        f"Recall:    {metrics.recall:.4f}"
    )
    print(
        f"F1:        {metrics.f1:.4f}"
    )
    print(
        f"PR-AUC:    {metrics.pr_auc:.4f}"
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

    print(
        "FRAME E02 — Hard Negative Evaluation"
    )
    print("=" * 45)

    print_metrics(
        "Transaction-only baseline",
        result.baseline,
    )

    print_metrics(
        "Graph-aware hybrid model",
        result.hybrid,
    )


if __name__ == "__main__":
    main()