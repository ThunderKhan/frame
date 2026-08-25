from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.risk.online import (
    build_online_feature_matrix,
)


def test_online_feature_matrix_shape() -> None:
    world = build_synthetic_world(
        legitimate_count=200,
        ring_count=1,
        ring_size=4,
        transactions_per_account=2,
        seed=42,
    )

    matrix = build_online_feature_matrix(
        world.transactions
    )

    assert matrix.shape == (
        len(world.transactions),
        14,
    )