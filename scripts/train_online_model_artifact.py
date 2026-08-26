from pathlib import Path

from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.risk.artifact import (
    RiskModelArtifact,
    save_risk_model_artifact,
)
from frame.risk.online import (
    ONLINE_FEATURE_NAMES,
    train_online_hybrid_model,
)

ARTIFACT_PATH = Path(
    "artifacts/frame_online_v1.pkl"
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

    artifact = RiskModelArtifact(
        model=model,
        feature_names=tuple(
            ONLINE_FEATURE_NAMES
        ),
        review_threshold=0.02,
        block_threshold=0.70,
    )

    save_risk_model_artifact(
        artifact,
        ARTIFACT_PATH,
    )

    print(
        "Saved FRAME online model artifact:"
    )
    print(
        ARTIFACT_PATH
    )


if __name__ == "__main__":
    main()