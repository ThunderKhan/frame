from frame.evaluation.independent import (
    evaluate_independent_worlds,
)
from frame.evaluation.worlds import (
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

    test_world = build_synthetic_world(
        legitimate_count=5_000,
        ring_count=3,
        ring_size=8,
        transactions_per_account=4,
        seed=1337,
    )

    result = evaluate_independent_worlds(
        train_world,
        test_world,
    )

    print("FRAME E01")
    print("=" * 40)

    print("\nTransaction-only baseline")
    print(
        f"Precision: {result.baseline.precision:.4f}"
    )
    print(
        f"Recall:    {result.baseline.recall:.4f}"
    )
    print(
        f"F1:        {result.baseline.f1:.4f}"
    )
    print(
        f"PR-AUC:    {result.baseline.pr_auc:.4f}"
    )

    print("\nHybrid graph-aware model")
    print(
        f"Precision: {result.hybrid.precision:.4f}"
    )
    print(
        f"Recall:    {result.hybrid.recall:.4f}"
    )
    print(
        f"F1:        {result.hybrid.f1:.4f}"
    )
    print(
        f"PR-AUC:    {result.hybrid.pr_auc:.4f}"
    )


if __name__ == "__main__":
    main()