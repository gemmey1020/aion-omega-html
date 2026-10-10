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
CONFLICT_RESOLUTIONS = {"KEEP_OLD", "OVERRIDE", "SCOPE_SPLIT", "ONE_OFF_EXCEPTION"}
DERIVED_STATE_FILES = {
    "active-preferences.json": "rules",
    "candidates.json": "candidates",
    "conflicts.json": "conflicts",
    "superseded.json": "rules",
}


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


def _prepare_active_rule(rule: dict[str, Any], used_ids: set[str]) -> dict[str, Any]:
    if not isinstance(rule, dict):
        raise TypeError("rule must be a dictionary")
    _require_rule_fields(rule, "rule")
    if rule["origin"] not in ACTIVATABLE_ORIGINS:
        raise ValueError("only a Founder-authorized origin can activate a rule")

    active_rule = dict(rule)
    active_rule["id"] = _record_id(active_rule, "rule")
    if active_rule["id"] in used_ids:
        raise ValueError(f"rule id {active_rule['id']!r} already exists")
    active_rule.setdefault("created_at", _now())
    active_rule.setdefault("source_generation", None)
    active_rule["status"] = "active"
    active_rule.setdefault("supersedes", None)
    if not ACTIVE_RULE_FIELDS <= active_rule.keys():
        raise ValueError("active rule does not satisfy the required provenance contract")
    return active_rule


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
    learning = _ensure_learning_files(root)
    active_path = learning / "active-preferences.json"
    active_state = _read_state(active_path, "rules")
    superseded_state = _read_state(learning / "superseded.json", "rules")
    active_ids = {item.get("id") for item in active_state["rules"] if isinstance(item, dict)}
    superseded_ids = {item.get("id") for item in superseded_state["rules"] if isinstance(item, dict)}
    active_rule = _prepare_active_rule(rule, active_ids | superseded_ids)

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


def _active_rule_by_id(state: dict[str, Any], rule_id: str) -> dict[str, Any] | None:
    return next(
        (
            rule
            for rule in state["rules"]
            if isinstance(rule, dict) and rule.get("id") == rule_id and rule.get("status") == "active"
        ),
        None,
    )


def record_conflict(root: Path, conflict: dict) -> dict:
    """Record a caller-detected conflict without changing active preferences."""
    if not isinstance(conflict, dict):
        raise TypeError("conflict must be a dictionary")
    learning = _ensure_learning_files(root)
    state = _read_state(learning / "conflicts.json", "conflicts")
    active_state = _read_state(learning / "active-preferences.json", "rules")

    conflict_id = _record_id(conflict, "conflict")
    if any(item.get("id") == conflict_id for item in state["conflicts"] if isinstance(item, dict)):
        raise ValueError(f"conflict id {conflict_id!r} already exists")
    old_rule_id = conflict.get("old_rule_id")
    if not isinstance(old_rule_id, str) or not old_rule_id:
        raise ValueError("conflict old_rule_id must be a non-empty string")
    old_rule = _active_rule_by_id(active_state, old_rule_id)
    if old_rule is None:
        raise ValueError(f"conflict old rule {old_rule_id!r} must be active")

    proposed = conflict.get("proposed_rule")
    if not isinstance(proposed, dict):
        raise ValueError("conflict proposed_rule must be an object")
    _require_rule_fields(proposed, "proposed rule")
    if proposed["origin"] not in ACTIVATABLE_ORIGINS:
        raise ValueError("conflict proposed rule must have a Founder-authorized origin")
    proposed = dict(proposed)
    proposed["id"] = _record_id(proposed, "rule")
    used_rule_ids = {
        item.get("id")
        for filename, collection in (("active-preferences.json", "rules"), ("superseded.json", "rules"))
        for item in _read_state(learning / filename, collection)[collection]
        if isinstance(item, dict)
    }
    if proposed["id"] in used_rule_ids:
        raise ValueError(f"proposed rule id {proposed['id']!r} already exists")
    kind = conflict.get("kind")
    if kind not in {"potential", "direct"}:
        raise ValueError("conflict kind must be 'potential' or 'direct'")
    overlapping_scope = conflict.get("overlapping_scope")
    if not isinstance(overlapping_scope, dict):
        raise ValueError("conflict overlapping_scope must be an object")

    recorded = dict(conflict)
    recorded.update(
        {
            "id": conflict_id,
            "old_rule_id": old_rule_id,
            "old_rule_snapshot": dict(old_rule),
            "proposed_rule": proposed,
            "overlapping_scope": dict(overlapping_scope),
            "status": "unresolved",
            "recorded_at": _now(),
        }
    )
    state["conflicts"].append(recorded)
    _write_json(learning / "conflicts.json", state)
    append_event(root, {"type": "conflict_recorded", "conflict_id": conflict_id, "old_rule_id": old_rule_id, "kind": kind})
    return recorded


def record_exception(root: Path, exception: dict) -> dict:
    """Append a Founder-authorized exception scoped to one recorded generation."""
    if not isinstance(exception, dict):
        raise TypeError("exception must be a dictionary")
    _require_rule_fields(exception, "exception")
    if exception["origin"] not in ACTIVATABLE_ORIGINS:
        raise ValueError("only a Founder-authorized origin can record an exception")
    generation_id = exception.get("generation_id")
    if not isinstance(generation_id, str) or not generation_id:
        raise ValueError("exception generation_id must be a non-empty string")

    learning = _ensure_learning_files(root)
    generations = _read_jsonl(learning / "generation-history.jsonl")
    if not any(item.get("id") == generation_id for item in generations):
        raise ValueError(f"exception generation {generation_id!r} does not exist")
    path = learning / "exceptions.jsonl"
    existing = _read_jsonl(path)
    exception_id = _record_id(exception, "exception")
    if any(item.get("id") == exception_id for item in existing):
        raise ValueError(f"exception id {exception_id!r} already exists")
    recorded = dict(exception)
    recorded.update(
        {
            "id": exception_id,
            "generation_id": generation_id,
            "created_at": exception.get("created_at") or _now(),
            "status": "generation_only",
        }
    )
    _append_jsonl(path, recorded)
    append_event(
        root,
        {"type": "exception_recorded", "exception_id": exception_id, "generation_id": generation_id, "scope": recorded["scope"]},
    )
    return recorded


def resolve_conflict(root: Path, conflict_id: str, resolution: str, payload: dict | None = None) -> dict:
    """Apply one explicit Founder resolution to a previously recorded conflict."""
    if resolution not in CONFLICT_RESOLUTIONS:
        raise ValueError(f"resolution must be one of {', '.join(sorted(CONFLICT_RESOLUTIONS))}")
    if payload is not None and not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")

    learning = _ensure_learning_files(root)
    conflicts_path = learning / "conflicts.json"
    conflicts_state = _read_state(conflicts_path, "conflicts")
    conflict = next(
        (item for item in conflicts_state["conflicts"] if isinstance(item, dict) and item.get("id") == conflict_id),
        None,
    )
    if conflict is None:
        raise ValueError(f"conflict {conflict_id!r} does not exist")
    if conflict.get("status") != "unresolved":
        raise ValueError(f"conflict {conflict_id!r} is not unresolved")

    active_path = learning / "active-preferences.json"
    superseded_path = learning / "superseded.json"
    active_state = _read_state(active_path, "rules")
    superseded_state = _read_state(superseded_path, "rules")
    old_rule_id = conflict["old_rule_id"]
    old_rule = _active_rule_by_id(active_state, old_rule_id)
    if old_rule is None:
        raise ValueError(f"conflict old rule {old_rule_id!r} is no longer active")

    prepared_rules: list[dict[str, Any]] = []
    if resolution == "OVERRIDE":
        proposed = dict(conflict["proposed_rule"])
        if proposed["scope"] != old_rule["scope"]:
            raise ValueError("OVERRIDE replacement must have the same scope as the old rule; use SCOPE_SPLIT for scoped changes")
        proposed["supersedes"] = old_rule_id
        used_ids = {
            item.get("id")
            for collection in (active_state["rules"], superseded_state["rules"])
            for item in collection
            if isinstance(item, dict)
        }
        prepared_rules = [_prepare_active_rule(proposed, used_ids)]
    elif resolution == "SCOPE_SPLIT":
        split_rules = (payload or {}).get("split_rules")
        if not isinstance(split_rules, list) or len(split_rules) < 2:
            raise ValueError("SCOPE_SPLIT requires at least two replacement split_rules")
        old_scope = old_rule.get("scope", {})
        used_ids = {
            item.get("id")
            for collection in (active_state["rules"], superseded_state["rules"])
            for item in collection
            if isinstance(item, dict)
        }
        for split_rule in split_rules:
            prepared = dict(split_rule) if isinstance(split_rule, dict) else split_rule
            if not isinstance(prepared, dict):
                raise ValueError("each split_rule must be an object")
            split_scope = prepared.get("scope")
            if (
                not isinstance(split_scope, dict)
                or len(split_scope) <= len(old_scope)
                or any(split_scope.get(key) != value for key, value in old_scope.items())
            ):
                raise ValueError("each split_rule must have a strictly narrower scope than the old rule")
            prepared["supersedes"] = old_rule_id
            active_rule = _prepare_active_rule(prepared, used_ids)
            used_ids.add(active_rule["id"])
            prepared_rules.append(active_rule)
        scopes = [rule["scope"] for rule in prepared_rules]
        if len({json.dumps(scope, sort_keys=True) for scope in scopes}) != len(scopes):
            raise ValueError("SCOPE_SPLIT replacement scopes must be distinct")
    elif resolution == "ONE_OFF_EXCEPTION":
        exception = (payload or {}).get("exception")
        if not isinstance(exception, dict):
            raise ValueError("ONE_OFF_EXCEPTION requires an exception object")
        if not isinstance(exception.get("scope"), dict) or any(
            exception["scope"].get(key) != value for key, value in conflict["overlapping_scope"].items()
        ):
            raise ValueError("one-off exception scope must stay within the recorded conflict scope")

    if resolution == "ONE_OFF_EXCEPTION":
        exception = record_exception(root, payload["exception"])
        conflict["exception_id"] = exception["id"]
    elif resolution in {"OVERRIDE", "SCOPE_SPLIT"}:
        active_state["rules"] = [rule for rule in active_state["rules"] if rule.get("id") != old_rule_id]
        superseded_rule = dict(old_rule)
        superseded_rule.update({"status": "superseded", "superseded_at": _now(), "superseded_by": [rule["id"] for rule in prepared_rules]})
        superseded_state["rules"].append(superseded_rule)
        active_state["rules"].extend(prepared_rules)
        _write_json(superseded_path, superseded_state)
        _write_json(active_path, active_state)

    conflict.update({"status": "resolved", "resolution": resolution, "resolved_at": _now()})
    _write_json(conflicts_path, conflicts_state)
    append_event(root, {"type": "conflict_resolved", "conflict_id": conflict_id, "resolution": resolution, "old_rule_id": old_rule_id})
    return conflict


def create_snapshot(root: Path, snapshot_id: str) -> Path:
    """Capture derived learning files without including append-only histories."""
    if not isinstance(snapshot_id, str) or not snapshot_id or not snapshot_id[0].isalnum() or any(
        not (character.isalnum() or character in "-_.") for character in snapshot_id
    ):
        raise ValueError("snapshot_id must be a simple filename identifier")
    learning = _ensure_learning_files(root)
    snapshot_dir = learning / "snapshots"
    snapshot_path = snapshot_dir / f"{snapshot_id}.json"
    if snapshot_path.exists():
        raise ValueError(f"snapshot {snapshot_id!r} already exists")
    states = {
        filename: _read_state(learning / filename, collection)
        for filename, collection in DERIVED_STATE_FILES.items()
    }
    snapshot = {
        "schema_version": "1.0",
        "snapshot_id": snapshot_id,
        "created_at": _now(),
        "states": states,
    }
    _write_json(snapshot_path, snapshot)
    append_event(root, {"type": "learning_snapshot_created", "snapshot_id": snapshot_id})
    return snapshot_path


def restore_snapshot(root: Path, snapshot_path: Path) -> dict:
    """Restore derived learning state and append a rollback event, preserving logs."""
    learning = _ensure_learning_files(root)
    snapshots_dir = (learning / "snapshots").resolve()
    path = Path(snapshot_path).resolve()
    if not path.is_relative_to(snapshots_dir) or not path.is_file():
        raise ValueError("snapshot_path must identify a file inside learning/snapshots")
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read snapshot {path}: {exc}") from exc
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != "1.0" or not isinstance(snapshot.get("snapshot_id"), str):
        raise ValueError("snapshot has an unsupported schema")
    states = snapshot.get("states")
    if not isinstance(states, dict) or set(states) != set(DERIVED_STATE_FILES):
        raise ValueError("snapshot must contain exactly the derived learning state files")
    for filename, collection in DERIVED_STATE_FILES.items():
        state = states[filename]
        if not isinstance(state, dict) or not isinstance(state.get(collection), list):
            raise ValueError(f"snapshot state {filename} must contain a {collection} list")

    for filename, _collection in DERIVED_STATE_FILES.items():
        _write_json(learning / filename, states[filename])
    rollback = {
        "type": "learning_rollback",
        "snapshot_id": snapshot["snapshot_id"],
        "restored_at": _now(),
    }
    append_event(root, rollback)
    return {"snapshot_id": snapshot["snapshot_id"], "restored_at": rollback["restored_at"], "snapshot_path": str(path)}
