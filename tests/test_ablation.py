from frame.evaluation.ablation import (
    build_selected_feature_matrix,
)
from frame.evaluation.worlds import (
    build_synthetic_world,
)
from frame.graph.builder import (
    build_payment_graph,
)


def test_selected_feature_matrix_shape() -> None:
    world = build_synthetic_world(
        legitimate_count=100,
        ring_count=1,
        ring_size=4,
        transactions_per_account=2,
        seed=42,
    )

    graph = build_payment_graph(
        world.transactions
    )

    matrix = (
        build_selected_feature_matrix(
            world.transactions,
            graph,
            [
                "device_degree",
                "ip_degree",
            ],
        )
    )

    assert matrix.shape == (
        len(world.transactions),
        4,
    )