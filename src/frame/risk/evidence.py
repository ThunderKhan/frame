from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceType(StrEnum):
    SHARED_DEVICE = "shared_device"
    SHARED_IP = "shared_ip"
    DEVICE_BURST = "device_burst"
    IP_BURST = "ip_burst"
    CUSTOMER_BURST = "customer_burst"
    MULTI_CUSTOMER_DEVICE = "multi_customer_device"
    MULTI_CUSTOMER_IP = "multi_customer_ip"
    MULTI_MERCHANT_DEVICE = "multi_merchant_device"
    LARGE_COMPONENT = "large_component"


@dataclass(frozen=True)
class RiskEvidence:
    evidence_type: EvidenceType
    severity: float
    message: str
    value: float


def build_risk_evidence(
    graph_features: dict[str, float],
    temporal_features: dict[str, float],
) -> list[RiskEvidence]:
    evidence: list[RiskEvidence] = []

    device_degree = graph_features[
        "device_degree"
    ]
    ip_degree = graph_features[
        "ip_degree"
    ]
    component_size = graph_features[
        "component_size"
    ]

    device_transactions = temporal_features[
        "device_transactions_30m"
    ]
    ip_transactions = temporal_features[
        "ip_transactions_30m"
    ]
    customer_transactions = temporal_features[
        "customer_transactions_30m"
    ]
    device_customers = temporal_features[
        "device_customers_30m"
    ]
    ip_customers = temporal_features[
        "ip_customers_30m"
    ]
    device_merchants = temporal_features[
        "device_merchants_30m"
    ]

    if device_degree >= 2.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.SHARED_DEVICE
                ),
                severity=min(
                    device_degree / 5.0,
                    1.0,
                ),
                message=(
                    "Device is already linked to "
                    f"{int(device_degree)} customers"
                ),
                value=device_degree,
            )
        )

    if ip_degree >= 2.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.SHARED_IP
                ),
                severity=min(
                    ip_degree / 8.0,
                    1.0,
                ),
                message=(
                    "IP address is already linked to "
                    f"{int(ip_degree)} customers"
                ),
                value=ip_degree,
            )
        )

    if device_transactions >= 4.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.DEVICE_BURST
                ),
                severity=min(
                    device_transactions / 10.0,
                    1.0,
                ),
                message=(
                    f"{int(device_transactions)} "
                    "transactions used this device "
                    "within 30 minutes"
                ),
                value=device_transactions,
            )
        )

    if ip_transactions >= 5.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.IP_BURST
                ),
                severity=min(
                    ip_transactions / 12.0,
                    1.0,
                ),
                message=(
                    f"{int(ip_transactions)} "
                    "transactions originated from "
                    "this IP within 30 minutes"
                ),
                value=ip_transactions,
            )
        )

    if customer_transactions >= 4.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.CUSTOMER_BURST
                ),
                severity=min(
                    customer_transactions / 8.0,
                    1.0,
                ),
                message=(
                    f"Customer initiated "
                    f"{int(customer_transactions)} "
                    "transactions within 30 minutes"
                ),
                value=customer_transactions,
            )
        )

    if device_customers >= 2.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.MULTI_CUSTOMER_DEVICE
                ),
                severity=min(
                    device_customers / 5.0,
                    1.0,
                ),
                message=(
                    f"{int(device_customers)} "
                    "customers used the same device "
                    "within 30 minutes"
                ),
                value=device_customers,
            )
        )

    if ip_customers >= 3.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.MULTI_CUSTOMER_IP
                ),
                severity=min(
                    ip_customers / 8.0,
                    1.0,
                ),
                message=(
                    f"{int(ip_customers)} "
                    "customers used the same IP "
                    "within 30 minutes"
                ),
                value=ip_customers,
            )
        )

    if device_merchants >= 3.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.MULTI_MERCHANT_DEVICE
                ),
                severity=min(
                    device_merchants / 8.0,
                    1.0,
                ),
                message=(
                    f"Device interacted with "
                    f"{int(device_merchants)} "
                    "merchants within 30 minutes"
                ),
                value=device_merchants,
            )
        )

    if component_size >= 10.0:
        evidence.append(
            RiskEvidence(
                evidence_type=(
                    EvidenceType.LARGE_COMPONENT
                ),
                severity=min(
                    component_size / 50.0,
                    1.0,
                ),
                message=(
                    "Transaction touches a graph "
                    f"component containing "
                    f"{int(component_size)} entities"
                ),
                value=component_size,
            )
        )

    return sorted(
        evidence,
        key=lambda item: item.severity,
        reverse=True,
    )