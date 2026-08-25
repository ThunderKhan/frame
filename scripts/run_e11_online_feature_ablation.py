from __future__ import annotations

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from frame.evaluation.worlds import (
    build_hard_negative_world,
    build_synthetic_world,
)
from frame.risk.baseline import build_labels
from frame.risk.hybrid import HYBRID_FEATURE_NAMES
from frame.risk.online import build_online_feature_matrix


def train_model(
    features: np.ndarray,
    labels: np.ndarray,
) -> CalibratedClassifierCV:
    estimator = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    model = CalibratedClassifierCV(
        estimator=estimator,
        method="sigmoid",
        cv=5,
    )

    model.fit(
        features,
        labels,
    )

    return model


def feature_indices(
    excluded: set[str],
) -> list[int]:
    return [
        index
        for index, name in enumerate(
            HYBRID_FEATURE_NAMES
        )
        if name not in excluded
    ]


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

    train_features = build_online_feature_matrix(
        train_world.transactions
    )

    train_labels = build_labels(
        train_world.transactions
    )

    test_features = build_online_feature_matrix(
        test_world.transactions
    )

    test_labels = build_labels(
        test_world.transactions
    )

    experiments = {
        "full": set(),
        "no_customer_degree": {
            "customer_degree",
        },
        "no_ip_degree": {
            "ip_degree",
        },
        "no_component_size": {
            "component_size",
        },
        "no_customer_or_ip_degree": {
            "customer_degree",
            "ip_degree",
        },
        "no_three_suspect_features": {
            "customer_degree",
            "ip_degree",
            "component_size",
        },
    }

    print(
        "FRAME E11 — Online Feature Ablation"
    )
    print("=" * 72)

    print(
        f"\n{'Experiment':<32}"
        f"{'Features':>10}"
        f"{'PR-AUC':>12}"
    )

    print("-" * 56)

    for name, excluded in experiments.items():
        indices = feature_indices(
            excluded
        )

        model = train_model(
            train_features[:, indices],
            train_labels,
        )

        probabilities = (
            model.predict_proba(
                test_features[:, indices]
            )[:, 1]
        )

        pr_auc = average_precision_score(
            test_labels,
            probabilities,
        )

        print(
            f"{name:<32}"
            f"{len(indices):>10}"
            f"{pr_auc:>12.4f}"
        )


if __name__ == "__main__":
    main()