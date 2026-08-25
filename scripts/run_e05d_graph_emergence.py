from frame.evaluation.cost import CostModel
from frame.evaluation.sweep import (
    sweep_thresholds,
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
    build_online_graph_evidence_mask,
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

    model = train_online_hybrid_model(
        train_world.transactions
    )

    validation_features = (
        build_online_feature_matrix(
            validation_world.transactions
        )
    )

    validation_labels = build_labels(
        validation_world.transactions
    )

    validation_probabilities = (
        model.predict_proba(
            validation_features
        )[:, 1]
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=1000.0,
    )

    thresholds = [
        0.02,
        0.05,
        0.08,
        0.10,
        0.12,
        0.15,
        0.18,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
    ]

    sweep = sweep_thresholds(
        validation_labels,
        validation_probabilities,
        cost_model,
        thresholds=thresholds,
    )

    best = min(
        sweep,
        key=lambda point: point.total_cost,
    )

    locked_threshold = best.threshold

    test_features = (
        build_online_feature_matrix(
            test_world.transactions
        )
    )

    test_probabilities = (
        model.predict_proba(
            test_features
        )[:, 1]
    )

    evidence_mask = (
        build_online_graph_evidence_mask(
            test_world.transactions
        )
    )

    ring_ids = sorted(
        {
            transaction.fraud_ring_id
            for transaction
            in test_world.transactions
            if (
                transaction.is_fraud
                and transaction.fraud_ring_id
                is not None
            )
        }
    )

    ordered = sorted(
        zip(
            test_world.transactions,
            test_probabilities,
            evidence_mask,
            strict=True,
        ),
        key=lambda item: (
            item[0].timestamp,
            item[0].transaction_id,
        ),
    )

    print(
        "FRAME E05d — Graph-Backed "
        "Fraud Ring Emergence"
    )
    print("=" * 60)

    print(
        f"\nLocked threshold: "
        f"{locked_threshold:.3f}"
    )

    graph_backed_detected = 0

    first_graph_positions: list[int] = []

    for ring_id in ring_ids:
        ring = [
            item
            for item in ordered
            if item[0].fraud_ring_id
            == ring_id
        ]

        first_alert = next(
            (
                index
                for index, (
                    _transaction,
                    probability,
                    _evidence,
                ) in enumerate(
                    ring,
                    start=1,
                )
                if probability
                >= locked_threshold
            ),
            None,
        )

        first_graph_alert = next(
            (
                index
                for index, (
                    _transaction,
                    probability,
                    evidence,
                ) in enumerate(
                    ring,
                    start=1,
                )
                if (
                    probability
                    >= locked_threshold
                    and bool(evidence)
                )
            ),
            None,
        )

        print(f"\n{ring_id}")
        print(
            "Fraud transactions: "
            f"{len(ring)}"
        )
        print(
            "First classifier alert: "
            f"{first_alert}"
        )
        print(
            "First graph-backed alert: "
            f"{first_graph_alert}"
        )

        if first_graph_alert is not None:
            graph_backed_detected += 1

            first_graph_positions.append(
                first_graph_alert
            )

    print("\nSummary")
    print("=" * 30)

    print(
        "Rings with graph-backed detection: "
        f"{graph_backed_detected}/"
        f"{len(ring_ids)}"
    )

    if first_graph_positions:
        average_position = (
            sum(first_graph_positions)
            / len(first_graph_positions)
        )

        print(
            "Average fraud transaction "
            "position for graph-backed alert: "
            f"{average_position:.2f}"
        )


if __name__ == "__main__":
    main()