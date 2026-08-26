from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

import httpx

from frame.data.fraud import inject_device_farm
from frame.data.generator import (
    generate_legitimate_transactions,
)
from frame.domain.transaction import Transaction


DEFAULT_API_BASE = "http://127.0.0.1:8000"
DEFAULT_DELAY = 0.45
DEFAULT_PHASE_PAUSE = 2.0


@dataclass(frozen=True)
class DemoTransaction:
    transaction: Transaction
    phase: str


def build_demo_transactions() -> list[DemoTransaction]:
    """
    Build a high-signal synthetic coordinated-abuse demo.

    This is intentionally a demonstration scenario, not the
    benchmark configuration.

    The model and policy are unchanged.

    Demo ring:
        - 5 customers
        - 4 transactions per customer
        - 100% shared device
        - 100% shared IP

    Transactions are still streamed in exact chronological
    order, including legitimate activity interleaved with
    the planted ring.

    Ground-truth labels are used only to identify the demo
    window. They are never sent to the scoring API.
    """

    legitimate = generate_legitimate_transactions(
        count=60,
        seed=2026,
    )

    world_transactions = inject_device_farm(
        legitimate,
        ring_id="demo_ring_001",
        ring_size=5,
        transactions_per_account=4,
        seed=3026,
        shared_device_ratio=1.0,
        shared_ip_ratio=1.0,
    )

    ordered = sorted(
        world_transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    fraud_positions = [
        index
        for index, transaction in enumerate(ordered)
        if transaction.is_fraud
    ]

    if not fraud_positions:
        raise RuntimeError(
            "Synthetic demo world contains no fraud transactions."
        )

    first_fraud_index = min(
        fraud_positions
    )

    last_fraud_index = max(
        fraud_positions
    )

    selected = ordered[
        : last_fraud_index + 1
    ]

    demo_transactions: list[
        DemoTransaction
    ] = []

    for index, transaction in enumerate(
        selected
    ):
        phase = (
            "BASELINE"
            if index < first_fraud_index
            else "COORDINATION"
        )

        demo_transactions.append(
            DemoTransaction(
                transaction=transaction,
                phase=phase,
            )
        )

    return demo_transactions


def transaction_payload(
    transaction: Transaction,
) -> dict[str, object]:
    """
    Convert an internal synthetic transaction into the
    public scoring payload.

    Ground-truth fraud labels are deliberately excluded.
    """

    return transaction.model_dump(
        mode="json",
        exclude={
            "is_fraud",
            "fraud_ring_id",
        },
    )


def print_phase_header(
    title: str,
    subtitle: str,
) -> None:
    print()
    print("=" * 72)
    print(title)
    print(subtitle)
    print("=" * 72)
    print()


def ensure_clean_state(
    client: httpx.Client,
    allow_dirty_state: bool,
) -> None:
    response = client.get(
        "/api/v1/stats",
    )

    response.raise_for_status()

    stats = response.json()

    transactions_scored = int(
        stats.get(
            "transactions_scored",
            0,
        )
    )

    if (
        transactions_scored > 0
        and not allow_dirty_state
    ):
        print()
        print(
            "FRAME DEMO STATE IS NOT CLEAN"
        )
        print("=" * 72)

        print(
            f"Existing transactions scored: "
            f"{transactions_scored}"
        )

        print()
        print(
            "Restart the FastAPI backend before a clean demo:"
        )
        print()

        print(
            "python -m uvicorn "
            "frame.api.app:app --reload"
        )

        print()
        print(
            "Development override:"
        )
        print()

        print(
            "python scripts\\stream_demo_transactions.py "
            "--allow-dirty-state"
        )

        print()

        raise SystemExit(1)


def get_evidence(
    result: dict[str, object],
) -> list[dict[str, object]]:
    raw_evidence = result.get(
        "evidence",
        [],
    )

    if not isinstance(
        raw_evidence,
        list,
    ):
        return []

    evidence: list[
        dict[str, object]
    ] = []

    for item in raw_evidence:
        if isinstance(
            item,
            dict,
        ):
            evidence.append(
                item
            )

    return evidence


def print_transaction_result(
    index: int,
    total: int,
    transaction: Transaction,
    result: dict[str, object],
) -> None:
    action = str(
        result["action"]
    )

    risk_score = float(
        result["risk_score"]
    )

    evidence = get_evidence(
        result
    )

    marker = {
        "ALLOW": "   ",
        "REVIEW": ">>>",
        "BLOCK": "XXX",
    }.get(
        action,
        "---",
    )

    print(
        f"{marker} "
        f"{index:03d}/{total:03d} "
        f"{transaction.transaction_id:<18} "
        f"risk={risk_score:0.3f} "
        f"action={action:<6} "
        f"signals={len(evidence):02d}"
    )

    if action not in {
        "REVIEW",
        "BLOCK",
    }:
        return

    for item in evidence:
        evidence_type = str(
            item.get(
                "type",
                "signal",
            )
        )

        message = str(
            item.get(
                "message",
                "",
            )
        )

        print(
            "      "
            f"- {evidence_type}: "
            f"{message}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the high-signal FRAME live fraud-ring demo."
        ),
    )

    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help=(
            "FRAME API base URL "
            f"(default: {DEFAULT_API_BASE})"
        ),
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=(
            "Delay between transactions in seconds "
            f"(default: {DEFAULT_DELAY})"
        ),
    )

    parser.add_argument(
        "--phase-pause",
        type=float,
        default=DEFAULT_PHASE_PAUSE,
        help=(
            "Pause when coordinated activity begins "
            f"(default: {DEFAULT_PHASE_PAUSE}s)"
        ),
    )

    parser.add_argument(
        "--allow-dirty-state",
        action="store_true",
        help=(
            "Allow streaming into an API that already "
            "contains scored transactions."
        ),
    )

    args = parser.parse_args()

    if args.delay < 0:
        parser.error(
            "--delay cannot be negative"
        )

    if args.phase_pause < 0:
        parser.error(
            "--phase-pause cannot be negative"
        )

    demo_transactions = (
        build_demo_transactions()
    )

    baseline_count = sum(
        item.phase == "BASELINE"
        for item in demo_transactions
    )

    coordination_count = sum(
        item.phase == "COORDINATION"
        for item in demo_transactions
    )

    print()
    print(
        "FRAME LIVE FRAUD-RING DEMO"
    )
    print("=" * 72)

    print(
        f"API:                {args.api_base}"
    )

    print(
        f"Baseline window:    {baseline_count}"
    )

    print(
        f"Coordination window:{coordination_count:>5}"
    )

    print(
        f"Total streamed:     {len(demo_transactions)}"
    )

    print(
        f"Transaction gap:    {args.delay:.2f}s"
    )

    print()
    print(
        "DEMO SCENARIO:"
    )

    print(
        "  ring customers   : 5"
    )

    print(
        "  tx per customer  : 4"
    )

    print(
        "  shared device    : 100%"
    )

    print(
        "  shared IP        : 100%"
    )

    print("=" * 72)

    highest_risk = 0.0
    review_count = 0
    block_count = 0

    try:
        with httpx.Client(
            base_url=args.api_base,
            timeout=10.0,
        ) as client:
            health_response = client.get(
                "/health",
            )

            health_response.raise_for_status()

            ensure_clean_state(
                client,
                allow_dirty_state=(
                    args.allow_dirty_state
                ),
            )

            print()
            print(
                "FRAME API ONLINE // "
                "DEMO STATE CLEAN"
            )

            print_phase_header(
                "PHASE 01 /// NORMAL TRAFFIC",
                (
                    "FRAME observes ordinary payment activity "
                    "and builds relationship context."
                ),
            )

            current_phase = (
                "BASELINE"
            )

            for index, item in enumerate(
                demo_transactions,
                start=1,
            ):
                if (
                    item.phase
                    == "COORDINATION"
                    and current_phase
                    != "COORDINATION"
                ):
                    time.sleep(
                        args.phase_pause
                    )

                    print_phase_header(
                        "PHASE 02 /// COORDINATION EMERGES",
                        (
                            "Five customers begin reusing the "
                            "same device and IP infrastructure."
                        ),
                    )

                    current_phase = (
                        "COORDINATION"
                    )

                transaction = (
                    item.transaction
                )

                response = client.post(
                    "/api/v1/risk/score",
                    json=transaction_payload(
                        transaction
                    ),
                )

                response.raise_for_status()

                result = (
                    response.json()
                )

                risk_score = float(
                    result[
                        "risk_score"
                    ]
                )

                action = str(
                    result[
                        "action"
                    ]
                )

                highest_risk = max(
                    highest_risk,
                    risk_score,
                )

                if action == "REVIEW":
                    review_count += 1

                if action == "BLOCK":
                    block_count += 1

                print_transaction_result(
                    index=index,
                    total=len(
                        demo_transactions
                    ),
                    transaction=transaction,
                    result=result,
                )

                time.sleep(
                    args.delay
                )

            final_stats_response = client.get(
                "/api/v1/stats",
            )

            final_stats_response.raise_for_status()

            final_stats = (
                final_stats_response.json()
            )

    except httpx.ConnectError:
        print()
        print(
            "Could not connect to FRAME API."
        )
        print()
        print(
            "Start the backend first:"
        )
        print()
        print(
            "python -m uvicorn "
            "frame.api.app:app --reload"
        )

        raise SystemExit(1)

    except httpx.HTTPStatusError as exc:
        print()
        print(
            "FRAME API returned an error:"
        )

        print(
            f"{exc.response.status_code} "
            f"{exc.response.text}"
        )

        raise SystemExit(1)

    print_phase_header(
        "PHASE 03 /// ANALYST HANDOFF",
        (
            "The synthetic coordination window ends and "
            "FRAME leaves the suspicious cluster visible "
            "for analyst inspection."
        ),
    )

    print(
        "FINAL COMMAND-CENTER STATE"
    )

    print(
        f"  scored       : "
        f"{final_stats['transactions_scored']}"
    )

    print(
        f"  allow        : "
        f"{final_stats['allowed']}"
    )

    print(
        f"  review       : "
        f"{final_stats['reviewed']}"
    )

    print(
        f"  block        : "
        f"{final_stats['blocked']}"
    )

    print(
        f"  highest risk : "
        f"{highest_risk:.3f}"
    )

    print(
        f"  graph nodes  : "
        f"{final_stats['graph_nodes']}"
    )

    print(
        f"  graph edges  : "
        f"{final_stats['graph_edges']}"
    )

    print()
    print(
        "DEMO DECISIONS"
    )

    print(
        f"  reviews seen : "
        f"{review_count}"
    )

    print(
        f"  blocks seen  : "
        f"{block_count}"
    )

    print()

    if block_count == 0:
        print(
            "WARNING /// NO BLOCK DECISION OCCURRED"
        )

        print(
            "Do not present this run as a BLOCK demo."
        )
    else:
        print(
            "XXX HIGH-RISK COORDINATION INTERCEPTED"
        )

    print()
    print(
        ">>> KEEP THE DASHBOARD OPEN"
    )

    print(
        ">>> INSPECT THE RED SHARED-INFRASTRUCTURE CLUSTER"
    )

    print(
        ">>> REVIEW THE LATEST REVIEW / BLOCK DECISIONS"
    )

    print()


if __name__ == "__main__":
    main()