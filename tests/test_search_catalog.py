import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_ENTRY = {
    "family": "evidence",
    "roles": ["evidence"],
    "profiles": ["silver"],
    "density": "medium",
    "motion": "low",
    "audiences": ["technical"],
    "keywords": ["payment"],
    "manifest": "library/evidence/sample/manifest.json",
}


def write_catalog(path: Path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def entry(pattern_id, **updates):
    return dict(BASE_ENTRY, id=pattern_id, **updates)


def run_search(catalog, *args):
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "search-catalog.py"), "--catalog", str(catalog), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_exact_role_and_profile_matches_rank_above_keyword_only(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [
            entry("pattern.role-profile", roles=["evidence"], profiles=["silver"], keywords=["payment"]),
            entry("pattern.keyword-only", roles=["summary"], profiles=["silver"], keywords=["payment"]),
        ],
    )

    result = run_search(catalog, "--profile", "silver", "--roles", "evidence", "--keywords", "payment")

    assert result.returncode == 0, result.stderr
    ranked = json.loads(result.stdout)
    assert ranked[0]["id"] == "pattern.role-profile"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_profile_filter_never_returns_nonmatching_patterns(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(catalog, [entry("silver.pattern"), entry("gold.pattern", profiles=["gold"])])

    result = run_search(catalog, "--profile", "silver")

    assert result.returncode == 0, result.stderr
    assert [row["id"] for row in json.loads(result.stdout)] == ["silver.pattern"]


def test_limit_caps_result_count(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(catalog, [entry(f"pattern-{i:02d}") for i in range(20)])

    result = run_search(catalog, "--profile", "silver", "--limit", "12")

    assert result.returncode == 0, result.stderr
    assert len(json.loads(result.stdout)) == 12


def test_no_match_returns_empty_json_array_and_success(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(catalog, [entry("pattern.one")])

    result = run_search(catalog, "--profile", "cyan", "--roles", "architecture")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []


def test_equal_scores_sort_stably_by_pattern_id(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(catalog, [entry("zeta"), entry("alpha"), entry("mu")])

    result = run_search(catalog, "--profile", "silver", "--roles", "evidence")

    assert result.returncode == 0, result.stderr
    assert [row["id"] for row in json.loads(result.stdout)] == ["alpha", "mu", "zeta"]


def test_semantic_query_excludes_profile_only_matches(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [
            entry("silver.profile-only", roles=["summary"], audiences=["board"], keywords=["finance"]),
            entry("silver.semantic", roles=["evidence"], audiences=["technical"], keywords=["payment"]),
        ],
    )

    result = run_search(catalog, "--profile", "silver", "--roles", "evidence")

    assert result.returncode == 0, result.stderr
    ranked = json.loads(result.stdout)
    assert [row["id"] for row in ranked] == ["silver.semantic"]
    assert ranked[0]["semantic_score"] > 0


def test_selected_profile_returns_native_rows_by_default(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [
            entry("silver.native", profiles=["silver"]),
            entry("cyan.non-native", profiles=["cyan"]),
        ],
    )

    result = run_search(catalog, "--profile", "silver", "--roles", "evidence")

    assert result.returncode == 0, result.stderr
    ranked = json.loads(result.stdout)
    assert [row["id"] for row in ranked] == ["silver.native"]
    assert ranked[0]["match_scope"] == "native"


def test_borrowed_rows_require_opt_in_and_semantic_relevance(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [
            entry("silver.native", profiles=["silver"], roles=["evidence"]),
            entry("cyan.borrowed-match", profiles=["cyan"], roles=["evidence"]),
            entry("cyan.borrowed-profile-only", profiles=["cyan"], roles=["summary"]),
        ],
    )

    default = run_search(catalog, "--profile", "silver", "--roles", "evidence")
    opted_in = run_search(
        catalog,
        "--profile",
        "silver",
        "--roles",
        "evidence",
        "--include-borrowed",
    )

    assert default.returncode == 0, default.stderr
    assert [row["id"] for row in json.loads(default.stdout)] == ["silver.native"]
    assert opted_in.returncode == 0, opted_in.stderr
    rows = json.loads(opted_in.stdout)
    assert [row["id"] for row in rows] == ["silver.native", "cyan.borrowed-match"]
    assert [row["match_scope"] for row in rows] == ["native", "borrowed"]
    assert rows[1]["semantic_score"] > 0


def test_borrowed_rows_are_capped_by_borrow_limit(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [entry(f"cyan.borrowed-{index}", profiles=["cyan"]) for index in range(5)],
    )

    result = run_search(
        catalog,
        "--profile",
        "silver",
        "--roles",
        "evidence",
        "--include-borrowed",
        "--borrow-limit",
        "2",
    )

    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == 2
    assert all(row["match_scope"] == "borrowed" for row in rows)


def test_native_rows_precede_borrowed_rows_when_borrowed_score_is_higher(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [
            entry("silver.native-weak", profiles=["silver"], roles=["evidence"], audiences=[], keywords=[]),
            entry("cyan.borrowed-strong", profiles=["cyan"], roles=["evidence"], audiences=["technical"], keywords=["payment"]),
        ],
    )

    result = run_search(
        catalog,
        "--profile",
        "silver",
        "--roles",
        "evidence",
        "--audiences",
        "technical",
        "--keywords",
        "payment",
        "--include-borrowed",
    )

    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert [row["id"] for row in rows] == ["silver.native-weak", "cyan.borrowed-strong"]
    assert rows[1]["semantic_score"] > rows[0]["semantic_score"]


def test_borrowed_rows_do_not_outrank_a_stronger_native_match(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(
        catalog,
        [
            entry("silver.native-strong", profiles=["silver"], roles=["evidence"], audiences=["technical"], keywords=["payment"]),
            entry("cyan.borrowed-weak", profiles=["cyan"], roles=["evidence"], audiences=[], keywords=[]),
        ],
    )

    result = run_search(
        catalog,
        "--profile",
        "silver",
        "--roles",
        "evidence",
        "--audiences",
        "technical",
        "--keywords",
        "payment",
        "--include-borrowed",
    )

    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert rows[0]["id"] == "silver.native-strong"
    assert rows[0]["semantic_score"] > rows[1]["semantic_score"]


def test_profile_browsing_without_semantic_query_is_stable_and_annotated(tmp_path):
    catalog = tmp_path / "catalog.ndjson"
    write_catalog(catalog, [entry("zeta"), entry("alpha"), entry("mu")])

    result = run_search(catalog, "--profile", "silver")

    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert [row["id"] for row in rows] == ["alpha", "mu", "zeta"]
    assert all(row["match_scope"] == "native" for row in rows)
    assert all(row["semantic_score"] == 0 for row in rows)


def test_malformed_catalog_and_negative_limits_fail_clearly(tmp_path):
    malformed = tmp_path / "malformed.ndjson"
    malformed.write_text('{"id": "broken"\n', encoding="utf-8")
    malformed_result = run_search(malformed)
    assert malformed_result.returncode == 2
    assert "malformed catalog JSON" in malformed_result.stderr

    catalog = tmp_path / "catalog.ndjson"
    write_catalog(catalog, [entry("silver.native")])
    negative_limit = run_search(catalog, "--limit", "-1")
    negative_borrow_limit = run_search(catalog, "--borrow-limit", "-1")
    assert negative_limit.returncode == 2
    assert "--limit" in negative_limit.stderr
    assert negative_borrow_limit.returncode == 2
    assert "--borrow-limit" in negative_borrow_limit.stderr
