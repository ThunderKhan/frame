from frame.evaluation.metrics import (
    evaluate_predictions,
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

    test_features = (
        build_online_feature_matrix(
            test_world.transactions
        )
    )

    labels = build_labels(
        test_world.transactions
    )

    probabilities = (
        model.predict_proba(
            test_features
        )[:, 1]
    )

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    metrics = evaluate_predictions(
        labels,
        predictions,
        probabilities,
    )

    print("FRAME E05 — Online Graph Evaluation")
    print("=" * 45)

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


if __name__ == "__main__":
    main()