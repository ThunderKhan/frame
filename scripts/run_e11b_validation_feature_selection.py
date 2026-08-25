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


def selected_indices(
    excluded: set[str],
) -> list[int]:
    return [
        index
        for index, feature_name in enumerate(
            HYBRID_FEATURE_NAMES
        )
        if feature_name not in excluded
    ]


def evaluate(
    train_features: np.ndarray,
    train_labels: np.ndarray,
    evaluation_features: np.ndarray,
    evaluation_labels: np.ndarray,
    excluded: set[str],
) -> float:
    indices = selected_indices(
        excluded
    )

    model = train_model(
        train_features[:, indices],
        train_labels,
    )

    probabilities = model.predict_proba(
        evaluation_features[:, indices]
    )[:, 1]

    return float(
        average_precision_score(
            evaluation_labels,
            probabilities,
        )
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

    train_features = build_online_feature_matrix(
        train_world.transactions
    )

    validation_features = build_online_feature_matrix(
        validation_world.transactions
    )

    test_features = build_online_feature_matrix(
        test_world.transactions
    )

    train_labels = build_labels(
        train_world.transactions
    )

    validation_labels = build_labels(
        validation_world.transactions
    )

    test_labels = build_labels(
        test_world.transactions
    )

    experiments: dict[
        str,
        set[str],
    ] = {
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

    validation_results: list[
        tuple[
            str,
            set[str],
            float,
        ]
    ] = []

    print(
        "FRAME E11b — Validation Feature Selection"
    )
    print("=" * 72)

    print(
        f"\n{'Experiment':<32}"
        f"{'Features':>10}"
        f"{'Validation PR-AUC':>20}"
    )

    print("-" * 62)

    for name, excluded in experiments.items():
        pr_auc = evaluate(
            train_features,
            train_labels,
            validation_features,
            validation_labels,
            excluded,
        )

        validation_results.append(
            (
                name,
                excluded,
                pr_auc,
            )
        )

        print(
            f"{name:<32}"
            f"{len(HYBRID_FEATURE_NAMES) - len(excluded):>10}"
            f"{pr_auc:>20.4f}"
        )

    selected_name, selected_excluded, selected_validation = max(
        validation_results,
        key=lambda item: item[2],
    )

    selected_test = evaluate(
        train_features,
        train_labels,
        test_features,
        test_labels,
        selected_excluded,
    )

    full_test = evaluate(
        train_features,
        train_labels,
        test_features,
        test_labels,
        set(),
    )

    print(
        "\nSELECTED ON VALIDATION"
    )
    print("=" * 40)

    print(
        f"Feature set:       "
        f"{selected_name}"
    )

    print(
        f"Excluded:          "
        f"{sorted(selected_excluded)}"
    )

    print(
        f"Validation PR-AUC: "
        f"{selected_validation:.4f}"
    )

    print(
        "\nLOCKED FINAL TEST"
    )
    print("=" * 40)

    print(
        f"Full model PR-AUC:     "
        f"{full_test:.4f}"
    )

    print(
        f"Selected model PR-AUC: "
        f"{selected_test:.4f}"
    )


if __name__ == "__main__":
    main()
    