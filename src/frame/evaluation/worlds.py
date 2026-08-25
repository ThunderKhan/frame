from __future__ import annotations

from dataclasses import dataclass

from frame.data.fraud import (
    inject_multiple_device_farms,
)
from frame.data.generator import (
    generate_legitimate_transactions,
)
from frame.domain.transaction import Transaction


@dataclass(frozen=True)
class SyntheticWorld:
    transactions: list[Transaction]
    seed: int
    legitimate_count: int
    ring_count: int


def build_synthetic_world(
    legitimate_count: int,
    ring_count: int,
    ring_size: int,
    transactions_per_account: int,
    seed: int,
) -> SyntheticWorld:
    legitimate = (
        generate_legitimate_transactions(
            count=legitimate_count,
            seed=seed,
        )
    )

    transactions = (
        inject_multiple_device_farms(
            legitimate,
            ring_count=ring_count,
            ring_size=ring_size,
            transactions_per_account=(
                transactions_per_account
            ),
            seed=seed + 1000,
            shared_device_ratio=0.8,
            shared_ip_ratio=0.7,
        )
    )

    return SyntheticWorld(
        transactions=transactions,
        seed=seed,
        legitimate_count=legitimate_count,
        ring_count=ring_count,
    )