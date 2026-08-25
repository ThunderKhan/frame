from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.risk.engine import (
    RiskEngine,
)
from frame.risk.online import (
    train_online_hybrid_model,
)
from frame.risk.policy import (
    RiskPolicy,
)


def main() -> None:
    train_world = build_synthetic_world(
        legitimate_count=10_000,
        ring_count=5,
        ring_size=8,
        transactions_per_account=4,
        seed=42,
    )

    demo_world = build_synthetic_world(
        legitimate_count=50,
        ring_count=1,
        ring_size=4,
        transactions_per_account=3,
        seed=2026,
    )

    model = train_online_hybrid_model(
        train_world.transactions
    )

    policy = RiskPolicy(
        review_threshold=0.05,
        block_threshold=0.90,
    )

    engine = RiskEngine(
        model=model,
        policy=policy,
    )

    ordered = sorted(
        demo_world.transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    for transaction in ordered:
        result = engine.score(
            transaction
        )

        if (
            result.action.value == "ALLOW"
            and not result.evidence
        ):
            continue

        print("\n" + "=" * 60)

        print(
            f"Transaction: "
            f"{result.transaction_id}"
        )

        print(
            f"Customer: "
            f"{transaction.customer_id}"
        )

        print(
            f"Risk score: "
            f"{result.probability:.4f}"
        )

        print(
            f"Action: "
            f"{result.action.value}"
        )

        if result.evidence:
            print("\nEvidence")

            for item in result.evidence:
                print(
                    f"- {item.message} "
                    f"(severity="
                    f"{item.severity:.2f})"
                )
        else:
            print(
                "\nEvidence: "
                "No coordination evidence"
            )


if __name__ == "__main__":
    main()