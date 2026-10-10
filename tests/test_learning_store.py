import importlib.util
import json
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "tools" / "learning-store.py"
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


@lru_cache(maxsize=1)
def learning_store():
    assert STORE_PATH.is_file(), "learning store module is not implemented"
    spec = importlib.util.spec_from_file_location("aion_learning_store", STORE_PATH)
    assert spec and spec.loader, "learning store module cannot be loaded"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def founder_rule(rule_id, scope, source_generation):
    return {
        "id": rule_id,
        "rule": f"Founder preference {rule_id}",
        "target": "composition density",
        "scope": scope,
        "origin": "founder_explicit",
        "source_generation": source_generation,
    }


def test_missing_learning_files_are_initialized_safely(tmp_path):
    store = learning_store()

    store.append_event(tmp_path, {"type": "session_started"})

    learning = tmp_path / "learning"
    for name in (
        "events.jsonl",
        "active-preferences.json",
        "candidates.json",
        "conflicts.json",
        "superseded.json",
        "exceptions.jsonl",
        "generation-history.jsonl",
    ):
        assert (learning / name).is_file(), name
    assert (learning / "snapshots").is_dir()
    assert read_json(learning / "active-preferences.json")["rules"] == []
    assert read_json(learning / "candidates.json")["candidates"] == []
    assert read_json(learning / "conflicts.json")["conflicts"] == []
    assert read_json(learning / "superseded.json")["rules"] == []


def test_event_ids_are_unique_and_existing_lines_are_append_only(tmp_path):
    store = learning_store()
    store.append_event(tmp_path, {"id": "event-1", "type": "founder_feedback"})
    events = tmp_path / "learning" / "events.jsonl"
    first_line = events.read_text(encoding="utf-8").splitlines()[0]

    store.append_event(tmp_path, {"type": "generation_completed"})

    lines = events.read_text(encoding="utf-8").splitlines()
    ids = [json.loads(line)["id"] for line in lines]
    assert lines[0] == first_line
    assert len(lines) == 2
    assert len(set(ids)) == 2
    with pytest.raises(ValueError, match="event id.*already exists"):
        store.append_event(tmp_path, {"id": "event-1", "type": "duplicate"})


def test_founder_rule_activation_has_complete_provenance(tmp_path):
    store = learning_store()

    active = store.activate_rule(tmp_path, founder_rule("rule-gold", {"profile": "gold"}, "gen-1"))

    assert ACTIVE_RULE_FIELDS <= active.keys()
    assert active["id"] == "rule-gold"
    assert active["status"] == "active"
    assert active["source_generation"] == "gen-1"
    assert active["origin"] == "founder_explicit"
    assert active["created_at"]
    assert read_json(tmp_path / "learning" / "active-preferences.json")["rules"] == [active]


def test_agent_inference_is_stored_as_candidate_not_active_rule(tmp_path):
    store = learning_store()
    candidate_input = {
        "id": "candidate-inferred",
        "rule": "Use a smaller opening panel",
        "target": "opening density",
        "scope": {"profile": "gold"},
        "origin": "agent_inference",
    }

    candidate = store.add_candidate(tmp_path, candidate_input)

    assert candidate["status"] == "candidate"
    assert candidate["origin"] == "agent_inference"
    assert read_json(tmp_path / "learning" / "candidates.json")["candidates"] == [candidate]
    assert read_json(tmp_path / "learning" / "active-preferences.json")["rules"] == []
    with pytest.raises(ValueError, match="Founder-authorized origin"):
        store.activate_rule(tmp_path, candidate_input)


def test_generation_history_appends_instead_of_replacing(tmp_path):
    store = learning_store()
    first = store.record_generation(tmp_path, {"id": "gen-1", "profile": "gold"})
    history = tmp_path / "learning" / "generation-history.jsonl"
    first_line = history.read_text(encoding="utf-8").splitlines()[0]

    second = store.record_generation(tmp_path, {"id": "gen-2", "profile": "silver"})

    lines = history.read_text(encoding="utf-8").splitlines()
    assert lines[0] == first_line
    assert [json.loads(line)["id"] for line in lines] == [first["id"], second["id"]]


def test_global_rules_apply_to_more_specific_queries(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("global", {}, "gen-global"))

    result = store.query_relevant(tmp_path, {"profile": "gold", "audience": "board"})

    assert [rule["id"] for rule in result["rules"]] == ["global"]


def test_profile_audience_and_artifact_type_scopes_require_matches(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("gold", {"profile": "gold"}, "gen-gold"))
    store.activate_rule(
        tmp_path,
        founder_rule("gold-board-report", {"profile": "gold", "audience": "board", "artifact_type": "report"}, "gen-board"),
    )

    matching = store.query_relevant(tmp_path, {"profile": "gold", "audience": "board", "artifact_type": "report"})
    wrong_profile = store.query_relevant(tmp_path, {"profile": "silver", "audience": "board", "artifact_type": "report"})
    wrong_artifact = store.query_relevant(tmp_path, {"profile": "gold", "audience": "board", "artifact_type": "presentation"})

    assert {rule["id"] for rule in matching["rules"]} == {"gold", "gold-board-report"}
    assert wrong_profile["rules"] == []
    assert [rule["id"] for rule in wrong_artifact["rules"]] == ["gold"]


def test_project_rules_do_not_leak_to_other_projects(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("project-a", {"project": "project-a"}, "gen-a"))

    matching = store.query_relevant(tmp_path, {"project": "project-a"})
    other_project = store.query_relevant(tmp_path, {"project": "project-b"})

    assert [rule["id"] for rule in matching["rules"]] == ["project-a"]
    assert other_project["rules"] == []


def test_narrower_rules_return_with_broader_provenance(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("global", {}, "gen-global"))
    store.activate_rule(tmp_path, founder_rule("gold", {"profile": "gold"}, "gen-gold"))
    store.activate_rule(
        tmp_path,
        founder_rule("gold-board", {"profile": "gold", "audience": "board"}, "gen-board"),
    )

    result = store.query_relevant(tmp_path, {"profile": "gold", "audience": "board"})

    assert [rule["id"] for rule in result["rules"]] == ["global", "gold", "gold-board"]
    assert [rule["source_generation"] for rule in result["rules"]] == ["gen-global", "gen-gold", "gen-board"]
    assert all(rule["origin"] == "founder_explicit" for rule in result["rules"])
