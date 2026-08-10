#!/usr/bin/env python3
"""Validate claim/evidence referential integrity and complete claim coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path

KB_PATH = Path(__file__).with_name("vibe_coding_knowledge_base.json")


def validate_claim_evidence(data: dict) -> list[str]:
    errors: list[str] = []

    for risk in data.get("risk_catalog", []):
        risk_id = risk.get("id", "<missing-risk-id>")
        claims = risk.get("what_can_go_wrong", [])
        evidence = risk.get("evidence", [])

        claim_ids = [claim.get("id") for claim in claims if isinstance(claim, dict)]
        if len(claim_ids) != len(set(claim_ids)):
            errors.append(f"{risk_id}: claim IDs must be unique within the risk")

        known_claim_ids = set(claim_ids)
        covered_claim_ids: set[str] = set()

        for record in evidence:
            evidence_id = record.get("id", "<missing-evidence-id>")
            for claim_id in record.get("supports_claim_ids", []):
                if claim_id not in known_claim_ids:
                    errors.append(
                        f"{risk_id}/{evidence_id}: dangling supports_claim_ids reference {claim_id!r}"
                    )
                else:
                    covered_claim_ids.add(claim_id)

        for claim_id in claim_ids:
            if claim_id not in covered_claim_ids:
                errors.append(f"{risk_id}: uncovered claim {claim_id!r}")

    return errors


def main() -> int:
    data = json.loads(KB_PATH.read_text(encoding="utf-8"))
    errors = validate_claim_evidence(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("PASS: all claim IDs are unique, all evidence references resolve, and all claims are covered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
