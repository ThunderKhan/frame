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

    def score(
        self,
        transaction: Transaction,
    ) -> RiskResult:
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
                [
                    transaction.amount,
                    float(
                        transaction.account_age_days
                    ),
                    graph_features[
                        "customer_degree"
                    ],
                    graph_features[
                        "card_degree"
                    ],
                    graph_features[
                        "device_degree"
                    ],
                    graph_features[
                        "ip_degree"
                    ],
                    graph_features[
                        "merchant_degree"
                    ],
                    graph_features[
                        "component_size"
                    ],
                    temporal_features[
                        "device_transactions_30m"
                    ],
                    temporal_features[
                        "ip_transactions_30m"
                    ],
                    temporal_features[
                        "customer_transactions_30m"
                    ],
                    temporal_features[
                        "device_customers_30m"
                    ],
                    temporal_features[
                        "ip_customers_30m"
                    ],
                    temporal_features[
                        "device_merchants_30m"
                    ],
                ]
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

        return RiskResult(
            transaction_id=(
                transaction.transaction_id
            ),
            probability=probability,
            action=action,
            evidence=tuple(evidence),
        )