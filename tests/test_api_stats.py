def test_empty_stats_contract() -> None:
    stats = {
        "transactions_scored": 0,
        "allowed": 0,
        "reviewed": 0,
        "blocked": 0,
        "average_risk_score": 0.0,
        "graph_nodes": 0,
        "graph_edges": 0,
    }

    assert (
        stats["transactions_scored"]
        == 0
    )

    assert (
        stats["average_risk_score"]
        == 0.0
    )