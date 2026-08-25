from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskAction(StrEnum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class RiskPolicy:
    review_threshold: float
    block_threshold: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.review_threshold <= 1.0:
            raise ValueError(
                "review_threshold must be between 0 and 1"
            )

        if not 0.0 <= self.block_threshold <= 1.0:
            raise ValueError(
                "block_threshold must be between 0 and 1"
            )

        if self.review_threshold >= self.block_threshold:
            raise ValueError(
                "review_threshold must be lower than block_threshold"
            )

    def decide(
        self,
        probability: float,
    ) -> RiskAction:
        if not 0.0 <= probability <= 1.0:
            raise ValueError(
                "probability must be between 0 and 1"
            )

        if probability >= self.block_threshold:
            return RiskAction.BLOCK

        if probability >= self.review_threshold:
            return RiskAction.REVIEW

        return RiskAction.ALLOW