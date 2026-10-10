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


def make_conflict(conflict_id="conflict-1", old_rule_id="old-rule", proposed_id="proposed-rule", scope=None):
    scope = {"profile": "gold", "audience": "board"} if scope is None else scope
    return {
        "id": conflict_id,
        "kind": "direct",
        "old_rule_id": old_rule_id,
        "proposed_rule": {
            "id": proposed_id,
            "rule": "Use a more expansive opening",
            "target": "opening density",
            "scope": dict(scope),
            "origin": "founder_explicit",
            "source_generation": "gen-new",
        },
        "overlapping_scope": dict(scope),
    }


def test_unresolved_conflict_does_not_mutate_active_preferences(tmp_path):
    store = learning_store()
    old = store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    before = read_json(tmp_path / "learning" / "active-preferences.json")["rules"]

    conflict = store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))

    after = read_json(tmp_path / "learning" / "active-preferences.json")["rules"]
    assert conflict["status"] == "unresolved"
    assert before == [old]
    assert after == before


def test_keep_old_leaves_the_active_rule_unchanged(tmp_path):
    store = learning_store()
    old = store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))

    resolved = store.resolve_conflict(tmp_path, "conflict-1", "KEEP_OLD")

    assert resolved["status"] == "resolved"
    assert resolved["resolution"] == "KEEP_OLD"
    assert read_json(tmp_path / "learning" / "active-preferences.json")["rules"] == [old]
    assert read_json(tmp_path / "learning" / "superseded.json")["rules"] == []


def test_override_supersedes_old_rule_and_activates_replacement(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))

    resolved = store.resolve_conflict(tmp_path, "conflict-1", "OVERRIDE")

    active = read_json(tmp_path / "learning" / "active-preferences.json")["rules"]
    superseded = read_json(tmp_path / "learning" / "superseded.json")["rules"]
    assert resolved["resolution"] == "OVERRIDE"
    assert [rule["id"] for rule in active] == ["proposed-rule"]
    assert active[0]["supersedes"] == "old-rule"
    assert len(superseded) == 1
    assert superseded[0]["id"] == "old-rule"
    assert superseded[0]["status"] == "superseded"


def test_scope_split_requires_replacements_before_superseding_old_rule(tmp_path):
    store = learning_store()
    old = store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))

    with pytest.raises(ValueError, match="split_rules"):
        store.resolve_conflict(tmp_path, "conflict-1", "SCOPE_SPLIT")

    assert read_json(tmp_path / "learning" / "active-preferences.json")["rules"] == [old]
    assert read_json(tmp_path / "learning" / "superseded.json")["rules"] == []
    assert read_json(tmp_path / "learning" / "conflicts.json")["conflicts"][0]["status"] == "unresolved"


def test_scope_split_supersedes_old_and_activates_supplied_scoped_rules(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))
    split_rules = [
        founder_rule("gold-board", {"profile": "gold", "audience": "board"}, "gen-board"),
        founder_rule("gold-client", {"profile": "gold", "audience": "client"}, "gen-client"),
    ]

    resolved = store.resolve_conflict(
        tmp_path,
        "conflict-1",
        "SCOPE_SPLIT",
        payload={"split_rules": split_rules},
    )

    active = read_json(tmp_path / "learning" / "active-preferences.json")["rules"]
    assert resolved["resolution"] == "SCOPE_SPLIT"
    assert {rule["id"] for rule in active} == {"gold-board", "gold-client"}
    assert all(rule["supersedes"] == "old-rule" for rule in active)
    assert [rule["id"] for rule in read_json(tmp_path / "learning" / "superseded.json")["rules"]] == ["old-rule"]


def test_one_off_exception_is_generation_scoped_and_keeps_old_rule(tmp_path):
    store = learning_store()
    old = store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    store.record_generation(tmp_path, {"id": "gen-one-off", "profile": "gold"})
    store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))
    exception = {
        "id": "exception-one-off",
        "generation_id": "gen-one-off",
        "rule": "Use a cinematic opening for this generation only",
        "target": "opening density",
        "scope": {"profile": "gold"},
        "origin": "founder_explicit",
    }

    resolved = store.resolve_conflict(
        tmp_path,
        "conflict-1",
        "ONE_OFF_EXCEPTION",
        payload={"exception": exception},
    )

    exceptions = [json.loads(line) for line in (tmp_path / "learning" / "exceptions.jsonl").read_text().splitlines()]
    assert resolved["resolution"] == "ONE_OFF_EXCEPTION"
    assert exceptions[0]["generation_id"] == "gen-one-off"
    assert read_json(tmp_path / "learning" / "active-preferences.json")["rules"] == [old]
    assert [rule["id"] for rule in store.query_relevant(tmp_path, {"profile": "gold"})["rules"]] == ["old-rule"]


def test_record_exception_requires_an_existing_generation_and_unique_id(tmp_path):
    store = learning_store()
    exception = {
        "id": "exception-direct",
        "generation_id": "gen-one-off",
        "rule": "Use a cinematic opening once",
        "target": "opening density",
        "scope": {"profile": "gold"},
        "origin": "founder_explicit",
    }

    with pytest.raises(ValueError, match="generation.*does not exist"):
        store.record_exception(tmp_path, exception)

    store.record_generation(tmp_path, {"id": "gen-one-off", "profile": "gold"})
    recorded = store.record_exception(tmp_path, exception)
    path = tmp_path / "learning" / "exceptions.jsonl"
    assert recorded["generation_id"] == "gen-one-off"
    assert [json.loads(line)["id"] for line in path.read_text().splitlines()] == ["exception-direct"]
    with pytest.raises(ValueError, match="exception id.*already exists"):
        store.record_exception(tmp_path, exception)


def test_override_cannot_expand_or_narrow_the_old_rule_scope_implicitly(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    conflict = make_conflict(scope={"profile": "gold", "audience": "board"})
    conflict["proposed_rule"]["scope"] = {"profile": "gold", "audience": "board"}
    store.record_conflict(tmp_path, conflict)

    with pytest.raises(ValueError, match="same scope"):
        store.resolve_conflict(tmp_path, "conflict-1", "OVERRIDE")

    assert [rule["id"] for rule in read_json(tmp_path / "learning" / "active-preferences.json")["rules"]] == ["old-rule"]
    assert read_json(tmp_path / "learning" / "superseded.json")["rules"] == []


def test_conflict_requires_an_active_old_rule(tmp_path):
    store = learning_store()

    with pytest.raises(ValueError, match="old rule.*must be active"):
        store.record_conflict(tmp_path, make_conflict())

    assert read_json(tmp_path / "learning" / "conflicts.json")["conflicts"] == []


def test_only_the_four_defined_conflict_resolutions_are_accepted(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("old-rule", {"profile": "gold"}, "gen-old"))
    store.record_conflict(tmp_path, make_conflict(scope={"profile": "gold"}))

    with pytest.raises(ValueError, match="resolution must be one of"):
        store.resolve_conflict(tmp_path, "conflict-1", "KEEP OLD")

    assert read_json(tmp_path / "learning" / "active-preferences.json")["rules"][0]["id"] == "old-rule"


def test_snapshot_restore_preserves_logs_and_unrelated_canon_files(tmp_path):
    store = learning_store()
    store.activate_rule(tmp_path, founder_rule("before-snapshot", {"profile": "gold"}, "gen-before"))
    store.add_candidate(
        tmp_path,
        {"id": "candidate-before", "rule": "Earlier observation", "target": "opening", "scope": {}, "origin": "repeated_observation"},
    )
    snapshot = store.create_snapshot(tmp_path, "before-change")
    protected_files = {
        "profiles/prime.json": "profile bytes",
        "library/marker.txt": "library bytes",
        "canon/canonical-dna.md": "canon bytes",
    }
    for relative, content in protected_files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    protected_before = {name: (tmp_path / name).read_bytes() for name in protected_files}

    store.activate_rule(tmp_path, founder_rule("after-snapshot", {"profile": "silver"}, "gen-after"))
    store.add_candidate(
        tmp_path,
        {"id": "candidate-after", "rule": "Later observation", "target": "opening", "scope": {}, "origin": "agent_inference"},
    )
    store.record_conflict(tmp_path, make_conflict("conflict-after", "before-snapshot", "proposed-after", {"profile": "gold"}))
    events_path = tmp_path / "learning" / "events.jsonl"
    events_before_restore = events_path.read_text(encoding="utf-8").splitlines()

    restored = store.restore_snapshot(tmp_path, snapshot)

    active = read_json(tmp_path / "learning" / "active-preferences.json")["rules"]
    candidates = read_json(tmp_path / "learning" / "candidates.json")["candidates"]
    events_after_restore = events_path.read_text(encoding="utf-8").splitlines()
    assert restored["snapshot_id"] == "before-change"
    assert [rule["id"] for rule in active] == ["before-snapshot"]
    assert [candidate["id"] for candidate in candidates] == ["candidate-before"]
    assert read_json(tmp_path / "learning" / "conflicts.json")["conflicts"] == []
    assert events_after_restore[: len(events_before_restore)] == events_before_restore
    assert json.loads(events_after_restore[-1])["type"] == "learning_rollback"
    assert len(events_after_restore) == len(events_before_restore) + 1
    assert {name: (tmp_path / name).read_bytes() for name in protected_files} == protected_before
    assert snapshot.is_file()
