import numpy as np

from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.risk.online import (
    train_online_hybrid_model,
)


FEATURE_NAMES = [
    "amount",
    "account_age_days",
    "customer_degree",
    "card_degree",
    "device_degree",
    "ip_degree",
    "merchant_degree",
    "component_size",
    "device_transactions_30m",
    "ip_transactions_30m",
    "customer_transactions_30m",
    "device_customers_30m",
    "ip_customers_30m",
    "device_merchants_30m",
]


def score(
    model,
    features: list[float],
) -> float:
    matrix = np.asarray(
        [features],
        dtype=float,
    )

    return float(
        model.predict_proba(matrix)[0, 1]
    )


def main() -> None:
    train_world = build_synthetic_world(
        legitimate_count=10_000,
        ring_count=5,
        ring_size=8,
        transactions_per_account=4,
        seed=42,
    )

    model = train_online_hybrid_model(
        train_world.transactions
    )

    baseline = [
        1000.0,  # amount
        300.0,   # account age
        4.0,     # customer degree
        1.0,     # card degree
        0.0,     # device degree
        0.0,     # ip degree
        20.0,    # merchant degree
        10.0,    # component size
        1.0,     # device tx 30m
        1.0,     # ip tx 30m
        1.0,     # customer tx 30m
        1.0,     # device customers 30m
        1.0,     # ip customers 30m
        1.0,     # device merchants 30m
    ]

    baseline_probability = score(
        model,
        baseline,
    )

    print(
        "FRAME E08 — Feature Sensitivity Audit"
    )
    print("=" * 60)

    print(
        f"\nBaseline probability: "
        f"{baseline_probability:.6f}"
    )

    probes = {
        "device_degree": [
            0.0,
            1.0,
            2.0,
            3.0,
            5.0,
            8.0,
        ],
        "ip_degree": [
            0.0,
            1.0,
            2.0,
            3.0,
            5.0,
            8.0,
        ],
        "component_size": [
            5.0,
            10.0,
            20.0,
            40.0,
            80.0,
        ],
        "device_customers_30m": [
            1.0,
            2.0,
            3.0,
            5.0,
            8.0,
        ],
        "ip_customers_30m": [
            1.0,
            2.0,
            3.0,
            5.0,
            8.0,
        ],
        "device_transactions_30m": [
            1.0,
            2.0,
            4.0,
            8.0,
            12.0,
        ],
    }

    for feature_name, values in probes.items():
        feature_index = FEATURE_NAMES.index(
            feature_name
        )

        print(
            f"\n{feature_name}"
        )
        print("-" * 40)

        for value in values:
            candidate = baseline.copy()

            candidate[
                feature_index
            ] = value

            probability = score(
                model,
                candidate,
            )

            print(
                f"{value:>8.2f}"
                f" -> {probability:.6f}"
            )


if __name__ == "__main__":
    main()