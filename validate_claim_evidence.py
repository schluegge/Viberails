#!/usr/bin/env python3
"""Validate claim IDs and claim-level evidence coverage in the Viberails KB."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    global_claim_ids: set[str] = set()
    evidence_ids: set[str] = set()

    for risk in data.get("risk_catalog", []):
        risk_id = risk.get("id", "<missing-risk-id>")
        claims = risk.get("what_can_go_wrong", [])
        claim_ids: set[str] = set()

        for claim in claims:
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                errors.append(f"{risk_id}: claim has missing/empty id")
                continue
            if claim_id in claim_ids:
                errors.append(f"{risk_id}: duplicate claim id {claim_id}")
            if claim_id in global_claim_ids:
                errors.append(f"global duplicate claim id {claim_id}")
            claim_ids.add(claim_id)
            global_claim_ids.add(claim_id)

        covered: set[str] = set()
        for evidence in risk.get("evidence", []):
            evidence_id = evidence.get("id")
            if isinstance(evidence_id, str) and evidence_id:
                if evidence_id in evidence_ids:
                    errors.append(f"duplicate evidence id {evidence_id}")
                evidence_ids.add(evidence_id)

            seen_in_record: set[str] = set()
            for support in evidence.get("supports_claims", []):
                claim_id = support.get("claim_id")
                if claim_id in seen_in_record:
                    errors.append(
                        f"{risk_id}/{evidence_id}: duplicate support for {claim_id}"
                    )
                seen_in_record.add(claim_id)
                if claim_id not in claim_ids:
                    errors.append(
                        f"{risk_id}/{evidence_id}: dangling claim reference {claim_id}"
                    )
                else:
                    covered.add(claim_id)

        for claim_id in sorted(claim_ids - covered):
            errors.append(f"{risk_id}: uncovered claim {claim_id}")

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vibe_coding_knowledge_base.json")
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: claim IDs are unique; all claim references resolve; every claim has evidence coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
