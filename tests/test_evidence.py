from frame.risk.evidence import (
    EvidenceType,
    build_risk_evidence,
)


def test_build_risk_evidence_detects_coordination() -> None:
    graph_features = {
        "customer_degree": 4.0,
        "card_degree": 1.0,
        "device_degree": 3.0,
        "ip_degree": 4.0,
        "merchant_degree": 20.0,
        "component_size": 18.0,
    }

    temporal_features = {
        "device_transactions_30m": 8.0,
        "ip_transactions_30m": 10.0,
        "customer_transactions_30m": 2.0,
        "device_customers_30m": 4.0,
        "ip_customers_30m": 5.0,
        "device_merchants_30m": 4.0,
    }

    evidence = build_risk_evidence(
        graph_features,
        temporal_features,
    )

    evidence_types = {
        item.evidence_type
        for item in evidence
    }

    assert (
        EvidenceType.SHARED_DEVICE
        in evidence_types
    )

    assert (
        EvidenceType.MULTI_CUSTOMER_DEVICE
        in evidence_types
    )

    assert (
        EvidenceType.MULTI_CUSTOMER_IP
        in evidence_types
    )

    assert evidence


def test_no_coordination_produces_little_evidence() -> None:
    graph_features = {
        "customer_degree": 0.0,
        "card_degree": 0.0,
        "device_degree": 0.0,
        "ip_degree": 0.0,
        "merchant_degree": 0.0,
        "component_size": 0.0,
    }

    temporal_features = {
        "device_transactions_30m": 1.0,
        "ip_transactions_30m": 1.0,
        "customer_transactions_30m": 1.0,
        "device_customers_30m": 1.0,
        "ip_customers_30m": 1.0,
        "device_merchants_30m": 1.0,
    }

    evidence = build_risk_evidence(
        graph_features,
        temporal_features,
    )

    assert evidence == []


def test_evidence_is_sorted_by_severity() -> None:
    graph_features = {
        "customer_degree": 4.0,
        "card_degree": 1.0,
        "device_degree": 4.0,
        "ip_degree": 2.0,
        "merchant_degree": 10.0,
        "component_size": 20.0,
    }

    temporal_features = {
        "device_transactions_30m": 8.0,
        "ip_transactions_30m": 5.0,
        "customer_transactions_30m": 1.0,
        "device_customers_30m": 3.0,
        "ip_customers_30m": 3.0,
        "device_merchants_30m": 3.0,
    }

    evidence = build_risk_evidence(
        graph_features,
        temporal_features,
    )

    severities = [
        item.severity
        for item in evidence
    ]

    assert severities == sorted(
        severities,
        reverse=True,
    )