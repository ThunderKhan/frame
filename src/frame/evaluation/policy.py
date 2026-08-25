from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from frame.risk.policy import (
    RiskAction,
    RiskPolicy,
)


@dataclass(frozen=True)
class PolicyMetrics:
    allowed: int
    reviewed: int
    blocked: int

    fraud_allowed: int
    fraud_reviewed: int
    fraud_blocked: int

    legitimate_allowed: int
    legitimate_reviewed: int
    legitimate_blocked: int


def evaluate_policy(
    labels: np.ndarray,
    probabilities: np.ndarray,
    policy: RiskPolicy,
) -> PolicyMetrics:
    if len(labels) != len(probabilities):
        raise ValueError(
            "labels and probabilities must have equal length"
        )

    allowed = 0
    reviewed = 0
    blocked = 0

    fraud_allowed = 0
    fraud_reviewed = 0
    fraud_blocked = 0

    legitimate_allowed = 0
    legitimate_reviewed = 0
    legitimate_blocked = 0

    for label, probability in zip(
        labels,
        probabilities,
        strict=True,
    ):
        action = policy.decide(
            float(probability)
        )

        is_fraud = bool(label)

        if action == RiskAction.ALLOW:
            allowed += 1

            if is_fraud:
                fraud_allowed += 1
            else:
                legitimate_allowed += 1

        elif action == RiskAction.REVIEW:
            reviewed += 1

            if is_fraud:
                fraud_reviewed += 1
            else:
                legitimate_reviewed += 1

        else:
            blocked += 1

            if is_fraud:
                fraud_blocked += 1
            else:
                legitimate_blocked += 1

    return PolicyMetrics(
        allowed=allowed,
        reviewed=reviewed,
        blocked=blocked,
        fraud_allowed=fraud_allowed,
        fraud_reviewed=fraud_reviewed,
        fraud_blocked=fraud_blocked,
        legitimate_allowed=legitimate_allowed,
        legitimate_reviewed=legitimate_reviewed,
        legitimate_blocked=legitimate_blocked,
    )