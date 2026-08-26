from pathlib import Path

from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.risk.artifact import (
    RiskModelArtifact,
    load_risk_model_artifact,
    save_risk_model_artifact,
)
from frame.risk.online import (
    ONLINE_FEATURE_NAMES,
    train_online_hybrid_model,
)


def test_risk_model_artifact_round_trip(
    tmp_path: Path,
) -> None:
    world = build_synthetic_world(
        legitimate_count=200,
        ring_count=1,
        ring_size=4,
        transactions_per_account=2,
        seed=42,
    )

    model = train_online_hybrid_model(
        world.transactions
    )

    artifact = RiskModelArtifact(
        model=model,
        feature_names=tuple(
            ONLINE_FEATURE_NAMES
        ),
        review_threshold=0.02,
        block_threshold=0.70,
    )

    path = tmp_path / "model.pkl"

    save_risk_model_artifact(
        artifact,
        path,
    )

    loaded = load_risk_model_artifact(
        path
    )

    assert loaded.feature_names == tuple(
        ONLINE_FEATURE_NAMES
    )

    assert loaded.review_threshold == 0.02
    assert loaded.block_threshold == 0.70