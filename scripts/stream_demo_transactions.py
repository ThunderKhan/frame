from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

import httpx

from frame.domain.transaction import (
    Transaction,
)
from frame.evaluation.worlds import (
    build_synthetic_world,
)


DEFAULT_API_BASE = "http://127.0.0.1:8000"
DEFAULT_DELAY = 0.45
DEFAULT_PHASE_PAUSE = 2.0
DEFAULT_BENIGN_COUNT = 18


@dataclass(frozen=True)
class DemoTransaction:
    transaction: Transaction
    phase: str


def build_demo_transactions(
    benign_count: int,
) -> list[DemoTransaction]:
    """
    Build a deliberately choreographed demo.

    The underlying synthetic world is unchanged. We only
    choose which transactions to stream and in what demo
    sequence they are presented.

    Sequence:
        1. Benign traffic establishes a normal baseline.
        2. Fraud-ring transactions arrive chronologically.
        3. The demo ends immediately after the ring sequence.

    Ground-truth labels are used only here to construct the
    synthetic demo. They are never sent to the risk API.
    """

    world = build_synthetic_world(
        legitimate_count=60,
        ring_count=1,
        ring_size=4,
        transactions_per_account=3,
        seed=2026,
    )

    ordered = sorted(
        world.transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    fraud_transactions = [
        transaction
        for transaction in ordered
        if transaction.is_fraud
    ]

    if not fraud_transactions:
        raise RuntimeError(
            "Synthetic demo world contains no fraud transactions."
        )

    first_fraud_timestamp = min(
        transaction.timestamp
        for transaction in fraud_transactions
    )

    benign_before_ring = [
        transaction
        for transaction in ordered
        if (
            not transaction.is_fraud
            and transaction.timestamp
            < first_fraud_timestamp
        )
    ]

    if len(benign_before_ring) < benign_count:
        raise RuntimeError(
            "Not enough benign transactions occur before "
            "the synthetic fraud ring for this demo."
        )

    selected_benign = benign_before_ring[
        -benign_count:
    ]

    selected_fraud = sorted(
        fraud_transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    demo_transactions = [
        DemoTransaction(
            transaction=transaction,
            phase="BASELINE",
        )
        for transaction in selected_benign
    ]

    demo_transactions.extend(
        DemoTransaction(
            transaction=transaction,
            phase="RING",
        )
        for transaction in selected_fraud
    )

    return demo_transactions


def transaction_payload(
    transaction: Transaction,
) -> dict[str, object]:
    """
    Convert an internal synthetic Transaction into the
    payload sent to FRAME.

    Synthetic ground-truth labels are deliberately excluded.
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
        print("FRAME DEMO STATE IS NOT CLEAN")
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
            "Then run this streamer again."
        )
        print()
        print(
            "For development only, you can bypass this check with:"
        )
        print()
        print(
            "python scripts\\stream_demo_transactions.py "
            "--allow-dirty-state"
        )
        print()

        raise SystemExit(1)


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

    evidence = result.get(
        "evidence",
        [],
    )

    if not isinstance(
        evidence,
        list,
    ):
        evidence = []

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
        if not isinstance(
            item,
            dict,
        ):
            continue

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
            "Run the choreographed FRAME live fraud-ring demo."
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
            "Pause before fraud-ring traffic begins "
            f"(default: {DEFAULT_PHASE_PAUSE}s)"
        ),
    )

    parser.add_argument(
        "--benign-count",
        type=int,
        default=DEFAULT_BENIGN_COUNT,
        help=(
            "Number of benign baseline transactions "
            f"(default: {DEFAULT_BENIGN_COUNT})"
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

    if args.benign_count < 1:
        parser.error(
            "--benign-count must be at least 1"
        )

    if args.delay < 0:
        parser.error(
            "--delay cannot be negative"
        )

    if args.phase_pause < 0:
        parser.error(
            "--phase-pause cannot be negative"
        )

    demo_transactions = (
        build_demo_transactions(
            benign_count=args.benign_count,
        )
    )

    baseline_count = sum(
        item.phase == "BASELINE"
        for item in demo_transactions
    )

    ring_count = sum(
        item.phase == "RING"
        for item in demo_transactions
    )

    print()
    print("FRAME LIVE FRAUD-RING DEMO")
    print("=" * 72)
    print(
        f"API:             {args.api_base}"
    )
    print(
        f"Baseline tx:     {baseline_count}"
    )
    print(
        f"Ring tx:         {ring_count}"
    )
    print(
        f"Total tx:        {len(demo_transactions)}"
    )
    print(
        f"Transaction gap: {args.delay:.2f}s"
    )
    print("=" * 72)

    try:
        with httpx.Client(
            base_url=args.api_base,
            timeout=10.0,
        ) as client:
            health_response = (
                client.get(
                    "/health",
                )
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
                    "Individual payments arrive without "
                    "obvious coordinated abuse."
                ),
            )

            current_phase = "BASELINE"

            for index, item in enumerate(
                demo_transactions,
                start=1,
            ):
                if (
                    item.phase == "RING"
                    and current_phase
                    != "RING"
                ):
                    time.sleep(
                        args.phase_pause
                    )

                    print_phase_header(
                        "PHASE 02 /// COORDINATION EMERGES",
                        (
                            "Shared infrastructure begins "
                            "connecting otherwise ordinary "
                            "customer activity."
                        ),
                    )

                    current_phase = "RING"

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

                result = response.json()

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

            final_stats_response = (
                client.get(
                    "/api/v1/stats",
                )
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
        "PHASE 03 /// RING INTERCEPTED",
        (
            "The demo stops here so the detected "
            "coordination remains visible in FRAME."
        ),
    )

    print(
        "FINAL COMMAND-CENTER STATE"
    )
    print(
        f"  scored : "
        f"{final_stats['transactions_scored']}"
    )
    print(
        f"  allow  : "
        f"{final_stats['allowed']}"
    )
    print(
        f"  review : "
        f"{final_stats['reviewed']}"
    )
    print(
        f"  block  : "
        f"{final_stats['blocked']}"
    )
    print(
        f"  nodes  : "
        f"{final_stats['graph_nodes']}"
    )
    print(
        f"  edges  : "
        f"{final_stats['graph_edges']}"
    )

    print()
    print(
        ">>> KEEP THE DASHBOARD OPEN"
    )
    print(
        ">>> REVIEW THE LIVE GRAPH "
        "AND RECENT DECISIONS"
    )
    print()


if __name__ == "__main__":
    main()