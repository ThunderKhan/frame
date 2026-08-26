from __future__ import annotations

import networkx as nx
import numpy as np
from sklearn.calibration import (
    CalibratedClassifierCV,
)

from frame.domain.transaction import (
    Transaction,
)
from frame.graph.builder import (
    add_transaction_to_graph,
)
from frame.graph.online import (
    extract_online_graph_features,
)
from frame.graph.temporal_online import (
    OnlineTemporalState,
)
from frame.risk.evidence import (
    build_risk_evidence,
)
from frame.risk.online import (
    build_online_feature_row,
)
from frame.risk.policy import (
    RiskPolicy,
)
from frame.risk.result import (
    RiskResult,
)


class RiskEngine:
    def __init__(
        self,
        model: CalibratedClassifierCV,
        policy: RiskPolicy,
        window_minutes: int = 30,
    ) -> None:
        self.model = model
        self.policy = policy

        self.graph = nx.Graph()

        self.temporal_state = (
            OnlineTemporalState(
                window_minutes=window_minutes
            )
        )

        self.results: list[
            RiskResult
        ] = []

        # Keep the scored transaction context so
        # investigation endpoints can map a decision
        # back to graph entities.
        self.transactions: dict[
            str,
            Transaction,
        ] = {}

    def score(
        self,
        transaction: Transaction,
    ) -> RiskResult:
        if (
            transaction.transaction_id
            in self.transactions
        ):
            raise ValueError(
                "duplicate transaction_id: "
                f"{transaction.transaction_id}"
            )

        graph_features = (
            extract_online_graph_features(
                transaction,
                self.graph,
            )
        )

        temporal_features = (
            self.temporal_state.extract_and_update(
                transaction
            )
        )

        feature_vector = np.asarray(
            [
                build_online_feature_row(
                    transaction,
                    graph_features,
                    temporal_features,
                )
            ],
            dtype=float,
        )

        probability = float(
            self.model.predict_proba(
                feature_vector
            )[0, 1]
        )

        action = self.policy.decide(
            probability
        )

        evidence = build_risk_evidence(
            graph_features,
            temporal_features,
        )

        add_transaction_to_graph(
            self.graph,
            transaction,
        )

        result = RiskResult(
            transaction_id=(
                transaction.transaction_id
            ),
            probability=probability,
            action=action,
            evidence=tuple(evidence),
        )

        self.results.append(
            result
        )

        self.transactions[
            transaction.transaction_id
        ] = transaction

        return result