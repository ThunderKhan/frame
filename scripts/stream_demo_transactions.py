from __future__ import annotations

import argparse
import time

import httpx

from frame.evaluation.worlds import (
    build_synthetic_world,
)


DEFAULT_API_BASE = "http://127.0.0.1:8000"


def build_demo_transactions():
    world = build_synthetic_world(
        legitimate_count=60,
        ring_count=1,
        ring_size=4,
        transactions_per_account=3,
        seed=2026,
    )

    transactions = sorted(
        world.transactions,
        key=lambda transaction: (
            transaction.timestamp,
            transaction.transaction_id,
        ),
    )

    return transactions


def transaction_payload(transaction):
    return transaction.model_dump(
        mode="json",
        exclude={
            "is_fraud",
            "fraud_ring_id",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stream a small synthetic transaction world "
            "into the FRAME Risk API."
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
        default=0.35,
        help=(
            "Delay between transactions in seconds "
            "(default: 0.35)"
        ),
    )

    args = parser.parse_args()

    transactions = build_demo_transactions()

    print()
    print("FRAME LIVE DEMO STREAM")
    print("=" * 60)
    print(f"API: {args.api_base}")
    print(f"Transactions: {len(transactions)}")
    print(f"Delay: {args.delay:.2f}s")
    print("=" * 60)
    print()

    try:
        with httpx.Client(
            base_url=args.api_base,
            timeout=10.0,
        ) as client:
            health_response = client.get(
                "/health",
            )
            health_response.raise_for_status()

            print("FRAME API online.")
            print()

            for index, transaction in enumerate(
                transactions,
                start=1,
            ):
                response = client.post(
                    "/api/v1/risk/score",
                    json=transaction_payload(
                        transaction,
                    ),
                )

                response.raise_for_status()

                result = response.json()

                action = result["action"]
                risk_score = float(
                    result["risk_score"],
                )

                evidence = result.get(
                    "evidence",
                    [],
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
                    f"{index:03d}/{len(transactions):03d} "
                    f"{transaction.transaction_id:<20} "
                    f"risk={risk_score:0.3f} "
                    f"action={action:<6} "
                    f"signals={len(evidence):02d}"
                )

                if action in {
                    "REVIEW",
                    "BLOCK",
                }:
                    for item in evidence:
                        print(
                            "      "
                            f"- {item['type']}: "
                            f"{item['message']}"
                        )

                time.sleep(
                    max(
                        0.0,
                        args.delay,
                    ),
                )

    except httpx.ConnectError:
        print()
        print(
            "Could not connect to FRAME API."
        )
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

    print()
    print("=" * 60)
    print("STREAM COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()