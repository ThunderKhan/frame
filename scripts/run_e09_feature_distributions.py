from __future__ import annotations

import numpy as np

from frame.evaluation.worlds import (
    build_hard_negative_world,
)
from frame.risk.baseline import (
    build_labels,
)
from frame.risk.hybrid import (
    HYBRID_FEATURE_NAMES,
)
from frame.risk.online import (
    build_online_feature_matrix,
)


def summarize(
    values: np.ndarray,
) -> tuple[
    float,
    float,
    float,
    float,
    float,
]:
    return (
        float(np.mean(values)),
        float(np.median(values)),
        float(np.percentile(values, 25)),
        float(np.percentile(values, 75)),
        float(np.max(values)),
    )


def main() -> None:
    world = build_hard_negative_world(
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

    features = build_online_feature_matrix(
        world.transactions
    )

    labels = build_labels(
        world.transactions
    )

    legitimate = features[
        labels == 0
    ]

    fraud = features[
        labels == 1
    ]

    print(
        "FRAME E09 — On-Data Feature Distribution Audit"
    )
    print("=" * 95)

    print(
        f"\nLegitimate transactions: "
        f"{len(legitimate)}"
    )

    print(
        f"Fraud transactions:      "
        f"{len(fraud)}"
    )

    header = (
        f"{'Feature':<30}"
        f"{'Class':<12}"
        f"{'Mean':>10}"
        f"{'Median':>10}"
        f"{'P25':>10}"
        f"{'P75':>10}"
        f"{'Max':>10}"
    )

    print("\n" + header)
    print("-" * len(header))

    for index, feature_name in enumerate(
        HYBRID_FEATURE_NAMES
    ):
        legitimate_stats = summarize(
            legitimate[:, index]
        )

        fraud_stats = summarize(
            fraud[:, index]
        )

        for class_name, stats in [
            ("legit", legitimate_stats),
            ("fraud", fraud_stats),
        ]:
            mean, median, p25, p75, maximum = stats

            print(
                f"{feature_name:<30}"
                f"{class_name:<12}"
                f"{mean:>10.3f}"
                f"{median:>10.3f}"
                f"{p25:>10.3f}"
                f"{p75:>10.3f}"
                f"{maximum:>10.3f}"
            )

        print()


if __name__ == "__main__":
    main()