from __future__ import annotations

from dataclasses import dataclass

from frame.risk.evidence import (
    RiskEvidence,
)
from frame.risk.policy import (
    RiskAction,
)


@dataclass(frozen=True)
class RiskResult:
    transaction_id: str
    probability: float
    action: RiskAction
    evidence: tuple[RiskEvidence, ...]