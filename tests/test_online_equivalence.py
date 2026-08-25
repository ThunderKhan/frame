from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.risk.online import (
    build_online_feature_matrix,
)


def test_online_feature_matrix_is_deterministic() -> None:
    world = build_synthetic_world(
        legitimate_count=500,
        ring_count=2,
        ring_size=4,
        transactions_per_account=2,
        seed=42,
    )

    first = build_online_feature_matrix(
        world.transactions
    )

    second = build_online_feature_matrix(
        world.transactions
    )

    assert first.shape == second.shape

    assert (
        first == second
    ).all()