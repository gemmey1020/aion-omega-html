#!/usr/bin/env python3
"""Mechanical, local-first storage for scoped AION learning."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


EMPTY_STATES = {
    "active-preferences.json": {"schema_version": "1.0", "rules": []},
    "candidates.json": {"schema_version": "1.0", "candidates": []},
    "conflicts.json": {"schema_version": "1.0", "conflicts": []},
    "superseded.json": {"schema_version": "1.0", "rules": []},
}
JSONL_FILES = ("events.jsonl", "exceptions.jsonl", "generation-history.jsonl")
ACTIVE_RULE_FIELDS = {
    "id",
    "rule",
    "target",
    "scope",
    "origin",
    "created_at",
    "source_generation",
    "status",
    "supersedes",
}
ACTIVATABLE_ORIGINS = {"founder_explicit", "founder_approved"}


def _learning_dir(root: Path) -> Path:
    return Path(root) / "learning"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ensure_learning_files(root: Path) -> Path:
    learning = _learning_dir(root)
    learning.mkdir(parents=True, exist_ok=True)
    (learning / "snapshots").mkdir(exist_ok=True)
    for name, initial in EMPTY_STATES.items():
        path = learning / name
        if not path.exists():
            _write_json(path, initial)
    for name in JSONL_FILES:
        path = learning / name
        if not path.exists():
            path.touch()
    return learning


def _write_json(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _read_state(path: Path, collection: str) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read learning state {path}: {exc}") from exc
    if not isinstance(state, dict) or not isinstance(state.get(collection), list):
        raise ValueError(f"learning state {path} must contain a {collection} list")
    return state


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read learning log {path}: {exc}") from exc
    records = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed learning JSON at {path}:{line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"learning record must be an object at {path}:{line_number}")
        records.append(record)
    return records


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    serialized = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as stream:
        if path.stat().st_size and not path.read_bytes().endswith(b"\n"):
            stream.write("\n")
        stream.write(serialized + "\n")


def _record_id(record: dict[str, Any], prefix: str) -> str:
    record_id = record.get("id")
    if record_id is None or record_id == "":
        return f"{prefix}-{uuid4().hex}"
    if not isinstance(record_id, str):
        raise ValueError(f"{prefix} id must be a string")
    return record_id


def _require_rule_fields(record: dict[str, Any], record_type: str) -> None:
    for field in ("rule", "target", "scope", "origin"):
        if field not in record:
            raise ValueError(f"{record_type} is missing required field: {field}")
    if not isinstance(record["rule"], str) or not record["rule"].strip():
        raise ValueError(f"{record_type} rule must be a non-empty string")
    if not isinstance(record["target"], str) or not record["target"].strip():
        raise ValueError(f"{record_type} target must be a non-empty string")
    if not isinstance(record["scope"], dict):
        raise ValueError(f"{record_type} scope must be an object")
    if not isinstance(record["origin"], str) or not record["origin"].strip():
        raise ValueError(f"{record_type} origin must be a non-empty string")


def append_event(root: Path, event: dict) -> None:
    """Append one unique event without rewriting prior event lines."""
    if not isinstance(event, dict):
        raise TypeError("event must be a dictionary")
    learning = _ensure_learning_files(root)
    path = learning / "events.jsonl"
    record = dict(event)
    record_id = _record_id(record, "event")
    existing_ids = {item.get("id") for item in _read_jsonl(path)}
    if record_id in existing_ids:
        raise ValueError(f"event id {record_id!r} already exists")
    record["id"] = record_id
    record.setdefault("created_at", _now())
    _append_jsonl(path, record)


def activate_rule(root: Path, rule: dict) -> dict:
    """Activate an explicitly Founder-authorized rule after caller-side conflict checks."""
    if not isinstance(rule, dict):
        raise TypeError("rule must be a dictionary")
    _require_rule_fields(rule, "rule")
    if rule["origin"] not in ACTIVATABLE_ORIGINS:
        raise ValueError("only a Founder-authorized origin can activate a rule")

    learning = _ensure_learning_files(root)
    active_path = learning / "active-preferences.json"
    active_state = _read_state(active_path, "rules")
    superseded_state = _read_state(learning / "superseded.json", "rules")
    active_ids = {item.get("id") for item in active_state["rules"] if isinstance(item, dict)}
    superseded_ids = {item.get("id") for item in superseded_state["rules"] if isinstance(item, dict)}
    active_rule = dict(rule)
    active_rule["id"] = _record_id(active_rule, "rule")
    if active_rule["id"] in active_ids | superseded_ids:
        raise ValueError(f"rule id {active_rule['id']!r} already exists")
    active_rule.setdefault("created_at", _now())
    active_rule.setdefault("source_generation", None)
    active_rule["status"] = "active"
    active_rule.setdefault("supersedes", None)
    if not ACTIVE_RULE_FIELDS <= active_rule.keys():
        raise ValueError("active rule does not satisfy the required provenance contract")

    active_state["rules"].append(active_rule)
    _write_json(active_path, active_state)
    append_event(
        root,
        {
            "type": "preference_activated",
            "rule_id": active_rule["id"],
            "origin": active_rule["origin"],
            "source_generation": active_rule["source_generation"],
            "scope": active_rule["scope"],
        },
    )
    return active_rule


def add_candidate(root: Path, candidate: dict) -> dict:
    """Store an unapproved observation or inference without activating it."""
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")
    _require_rule_fields(candidate, "candidate")
    learning = _ensure_learning_files(root)
    path = learning / "candidates.json"
    state = _read_state(path, "candidates")
    stored = dict(candidate)
    stored["id"] = _record_id(stored, "candidate")
    existing_ids = {item.get("id") for item in state["candidates"] if isinstance(item, dict)}
    if stored["id"] in existing_ids:
        raise ValueError(f"candidate id {stored['id']!r} already exists")
    stored.setdefault("created_at", _now())
    stored["status"] = "candidate"
    state["candidates"].append(stored)
    _write_json(path, state)
    append_event(
        root,
        {"type": "candidate_added", "candidate_id": stored["id"], "origin": stored["origin"], "scope": stored["scope"]},
    )
    return stored


def record_generation(root: Path, generation: dict) -> dict:
    """Append a generation receipt to history and return the stored record."""
    if not isinstance(generation, dict):
        raise TypeError("generation must be a dictionary")
    learning = _ensure_learning_files(root)
    path = learning / "generation-history.jsonl"
    record = dict(generation)
    record["id"] = _record_id(record, "generation")
    existing_ids = {item.get("id") for item in _read_jsonl(path)}
    if record["id"] in existing_ids:
        raise ValueError(f"generation id {record['id']!r} already exists")
    record.setdefault("created_at", _now())
    _append_jsonl(path, record)
    return record


def query_relevant(root: Path, scope: dict) -> dict:
    """Return active rules whose scopes are fully satisfied by the request scope.

    An empty rule scope is global. More specific matching rules follow broader
    rules, and each complete rule retains its origin and generation provenance.
    """
    if not isinstance(scope, dict):
        raise TypeError("scope must be a dictionary")
    learning = _ensure_learning_files(root)
    state = _read_state(learning / "active-preferences.json", "rules")
    matching = []
    for rule in state["rules"]:
        if not isinstance(rule, dict) or rule.get("status") != "active":
            continue
        rule_scope = rule.get("scope", {})
        if not isinstance(rule_scope, dict):
            continue
        if all(scope.get(key) == value for key, value in rule_scope.items()):
            matching.append(rule)
    matching.sort(key=lambda rule: (len(rule.get("scope", {})), str(rule.get("id", ""))))
    return {"scope": dict(scope), "rules": matching}
