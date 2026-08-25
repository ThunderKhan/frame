from frame.evaluation.ablation import (
    evaluate_ablation,
)
from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.graph.builder import (
    build_payment_graph,
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

    train_transactions = (
        train_world.transactions
    )
    test_transactions = (
        test_world.transactions
    )

    train_graph = build_payment_graph(
        train_transactions
    )
    test_graph = build_payment_graph(
        test_transactions
    )

    experiments = {
        "transaction-only": [],
        "device-only": [
            "device_degree",
        ],
        "ip-only": [
            "ip_degree",
        ],
        "device+ip": [
            "device_degree",
            "ip_degree",
        ],
        "full-graph": [
            "customer_degree",
            "card_degree",
            "device_degree",
            "ip_degree",
            "merchant_degree",
            "component_size",
        ],
    }

    print("FRAME E03 — Feature Ablation")
    print("=" * 45)

    for name, features in (
        experiments.items()
    ):
        result = evaluate_ablation(
            name=name,
            train_transactions=(
                train_transactions
            ),
            test_transactions=(
                test_transactions
            ),
            train_graph=train_graph,
            test_graph=test_graph,
            graph_feature_names=features,
        )

        print(f"\n{name}")
        print(
            "Precision: "
            f"{result.metrics.precision:.4f}"
        )
        print(
            "Recall:    "
            f"{result.metrics.recall:.4f}"
        )
        print(
            "F1:        "
            f"{result.metrics.f1:.4f}"
        )
        print(
            "PR-AUC:    "
            f"{result.metrics.pr_auc:.4f}"
        )


if __name__ == "__main__":
    main()