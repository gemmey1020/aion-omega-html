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
