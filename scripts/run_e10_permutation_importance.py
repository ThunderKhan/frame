from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
)

from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)
from frame.risk.baseline import (
    build_labels,
)
from frame.risk.hybrid import (
    HYBRID_FEATURE_NAMES,
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

    features = build_online_feature_matrix(
        test_world.transactions
    )

    labels = build_labels(
        test_world.transactions
    )

    baseline_probabilities = (
        model.predict_proba(
            features
        )[:, 1]
    )

    baseline_pr_auc = (
        average_precision_score(
            labels,
            baseline_probabilities,
        )
    )

    rng = np.random.default_rng(
        42
    )

    repeats = 10

    results: list[
        tuple[
            str,
            float,
            float,
        ]
    ] = []

    for feature_index, feature_name in enumerate(
        HYBRID_FEATURE_NAMES
    ):
        drops: list[float] = []

        for _ in range(repeats):
            shuffled = features.copy()

            shuffled[
                :,
                feature_index,
            ] = rng.permutation(
                shuffled[
                    :,
                    feature_index,
                ]
            )

            probabilities = (
                model.predict_proba(
                    shuffled
                )[:, 1]
            )

            shuffled_pr_auc = (
                average_precision_score(
                    labels,
                    probabilities,
                )
            )

            drops.append(
                baseline_pr_auc
                - shuffled_pr_auc
            )

        results.append(
            (
                feature_name,
                float(
                    np.mean(drops)
                ),
                float(
                    np.std(drops)
                ),
            )
        )

    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    print(
        "FRAME E10 — Permutation Importance"
    )
    print("=" * 72)

    print(
        f"\nBaseline PR-AUC: "
        f"{baseline_pr_auc:.4f}"
    )

    print(
        "\n"
        f"{'Feature':<30}"
        f"{'Mean PR-AUC drop':>20}"
        f"{'Std':>12}"
    )

    print("-" * 62)

    for (
        feature_name,
        mean_drop,
        std_drop,
    ) in results:
        print(
            f"{feature_name:<30}"
            f"{mean_drop:>20.4f}"
            f"{std_drop:>12.4f}"
        )


if __name__ == "__main__":
    main()