from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

from sklearn.calibration import CalibratedClassifierCV

from frame.risk.online import ONLINE_FEATURE_NAMES


@dataclass(frozen=True)
class RiskModelArtifact:
    model: CalibratedClassifierCV
    feature_names: tuple[str, ...]
    review_threshold: float
    block_threshold: float


def save_risk_model_artifact(
    artifact: RiskModelArtifact,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("wb") as file:
        pickle.dump(
            artifact,
            file,
        )


def load_risk_model_artifact(
    path: Path,
) -> RiskModelArtifact:
    with path.open("rb") as file:
        artifact = pickle.load(file)

    if not isinstance(
        artifact,
        RiskModelArtifact,
    ):
        raise TypeError(
            "invalid risk model artifact"
        )

    if artifact.feature_names != tuple(
        ONLINE_FEATURE_NAMES
    ):
        raise ValueError(
            "model artifact feature schema "
            "does not match runtime schema"
        )

    return artifact