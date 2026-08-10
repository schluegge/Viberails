#!/usr/bin/env python3
"""Validate risk applicability references against the declared Viberails scope."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    scope = data.get("scope", {})

    persona_ids: set[str] = set()
    for persona in scope.get("personas", []):
        persona_id = persona.get("id")
        if not isinstance(persona_id, str) or not persona_id:
            errors.append("scope.personas: persona has missing/empty id")
            continue
        if persona_id in persona_ids:
            errors.append(f"scope.personas: duplicate persona id {persona_id}")
        persona_ids.add(persona_id)

    platform_ids: set[str] = set()
    for platform_id in scope.get("platforms", []):
        if not isinstance(platform_id, str) or not platform_id:
            errors.append("scope.platforms: platform has missing/empty id")
            continue
        if platform_id in platform_ids:
            errors.append(f"scope.platforms: duplicate platform id {platform_id}")
        platform_ids.add(platform_id)

    for risk in data.get("risk_catalog", []):
        risk_id = risk.get("id", "<missing-risk-id>")
        for persona_id in risk.get("applies_to_personas", []):
            if persona_id not in persona_ids:
                errors.append(f"{risk_id}: dangling persona reference {persona_id}")
        for platform_id in risk.get("applies_to_platforms", []):
            if platform_id not in platform_ids:
                errors.append(f"{risk_id}: dangling platform reference {platform_id}")

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vibe_coding_knowledge_base.json")
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: scope persona/platform IDs are unique and all risk applicability references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
