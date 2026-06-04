from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

Rule = dict[str, Any]

RULE_FILE = Path(__file__).resolve().parents[1] / "data" / "audit_rules.json"


@lru_cache(maxsize=1)
def load_audit_rules() -> dict[str, Any]:
    with RULE_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload


def rules_for(kind: str) -> list[Rule]:
    rules = load_audit_rules().get(kind, [])
    return list(rules) if isinstance(rules, list) else []


def semantic_review_rules_for(kind: str) -> list[Rule]:
    semantic_rules = load_audit_rules().get("semantic_review", {})
    if not isinstance(semantic_rules, dict):
        return []
    rules = semantic_rules.get(kind, [])
    return list(rules) if isinstance(rules, list) else []