from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

Rule = dict[str, Any]

RULE_FILE = Path(__file__).resolve().parents[1] / "data" / "audit_rules.json"


_RULE_CACHE: Optional[dict[str, Any]] = None
_RULE_CACHE_MTIME: Optional[float] = None


def load_audit_rules() -> dict[str, Any]:
    global _RULE_CACHE, _RULE_CACHE_MTIME
    mtime = RULE_FILE.stat().st_mtime
    if _RULE_CACHE is None or _RULE_CACHE_MTIME != mtime:
        with RULE_FILE.open("r", encoding="utf-8") as file:
            _RULE_CACHE = json.load(file)
        _RULE_CACHE_MTIME = mtime
    assert _RULE_CACHE is not None
    return _RULE_CACHE


def rules_for(kind: str) -> list[Rule]:
    rules = load_audit_rules().get(kind, [])
    return list(rules) if isinstance(rules, list) else []


def semantic_review_rules_for(kind: str) -> list[Rule]:
    semantic_rules = load_audit_rules().get("semantic_review", {})
    if not isinstance(semantic_rules, dict):
        return []
    rules = semantic_rules.get(kind, [])
    return list(rules) if isinstance(rules, list) else []