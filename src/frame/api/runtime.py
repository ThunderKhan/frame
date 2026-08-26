from pathlib import Path

from frame.risk.artifact import (
    load_risk_model_artifact,
)
from frame.risk.engine import RiskEngine
from frame.risk.policy import RiskPolicy

DEFAULT_ARTIFACT_PATH = Path(
    "artifacts/frame_online_v1.pkl"
)


def build_risk_engine(
    artifact_path: Path = DEFAULT_ARTIFACT_PATH,
) -> RiskEngine:
    artifact = load_risk_model_artifact(
        artifact_path
    )

    policy = RiskPolicy(
        review_threshold=(
            artifact.review_threshold
        ),
        block_threshold=(
            artifact.block_threshold
        ),
    )

    return RiskEngine(
        model=artifact.model,
        policy=policy,
    )