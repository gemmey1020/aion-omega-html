import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALID_MANIFEST = {
    "id": "hero.sample",
    "family": "hero",
    "roles": ["summary"],
    "best_for": ["brief opening"],
    "avoid_when": ["dense evidence"],
    "density": "medium",
    "motion": "low",
    "profile_affinity": ["prime"],
    "capabilities": ["HTML/CSS"],
    "variant_axes": ["emphasis"],
    "reference": "reference.html",
}


def write_profiles(root: Path):
    profiles = root / "profiles"
    profiles.mkdir(parents=True, exist_ok=True)
    for profile_id in ("prime", "gold", "silver", "cyan"):
        (profiles / f"{profile_id}.json").write_text(
            json.dumps({"id": profile_id}), encoding="utf-8"
        )


def write_pattern(root: Path, dirname="sample", manifest=None, write_reference=True):
    write_profiles(root)
    pattern_dir = root / "library" / "hero" / dirname
    pattern_dir.mkdir(parents=True, exist_ok=True)
    data = dict(VALID_MANIFEST if manifest is None else manifest)
    (pattern_dir / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
    if write_reference:
        (pattern_dir / "reference.html").write_text("<!doctype html><title>sample</title>", encoding="utf-8")
    return pattern_dir


def write_catalog(root: Path, entries):
    catalog = root / "index" / "catalog.ndjson"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")


def catalog_entry(root: Path, pattern_dir, pattern_id=None):
    manifest_path = pattern_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "id": pattern_id or manifest["id"],
        "family": manifest["family"],
        "roles": manifest["roles"],
        "profiles": ["prime"],
        "density": manifest["density"],
        "motion": manifest["motion"],
        "audiences": ["founder"],
        "keywords": ["sample"],
        "manifest": manifest_path.relative_to(root).as_posix(),
    }


def run_validator(root: Path):
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate-library.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_duplicate_pattern_id_fails(tmp_path):
    first = write_pattern(tmp_path, "first")
    second = write_pattern(tmp_path, "second")
    write_catalog(tmp_path, [catalog_entry(tmp_path, first), catalog_entry(tmp_path, second)])

    result = run_validator(tmp_path)

    assert result.returncode != 0
    assert "duplicate id" in result.stdout.lower() + result.stderr.lower()


def test_malformed_manifest_json_names_the_path(tmp_path):
    pattern_dir = write_pattern(tmp_path)
    (pattern_dir / "manifest.json").write_text("{broken", encoding="utf-8")
    write_catalog(tmp_path, [])

    result = run_validator(tmp_path)

    assert result.returncode != 0
    assert "library/hero/sample/manifest.json" in result.stdout + result.stderr


def test_catalog_pointing_to_missing_pattern_fails(tmp_path):
    missing = {
        "id": "hero.missing",
        "family": "hero",
        "roles": ["summary"],
        "profiles": ["prime"],
        "density": "medium",
        "motion": "low",
        "audiences": ["founder"],
        "keywords": ["missing"],
        "manifest": "library/hero/missing/manifest.json",
    }
    write_catalog(tmp_path, [missing])

    result = run_validator(tmp_path)

    assert result.returncode != 0
    assert "missing pattern" in result.stdout.lower() + result.stderr.lower()


def test_manifest_referencing_invalid_profile_fails(tmp_path):
    manifest = dict(VALID_MANIFEST, profile_affinity=["prime", "unknown"])
    pattern_dir = write_pattern(tmp_path, manifest=manifest)
    write_catalog(tmp_path, [catalog_entry(tmp_path, pattern_dir)])

    result = run_validator(tmp_path)

    assert result.returncode != 0
    assert "invalid profile" in result.stdout.lower() + result.stderr.lower()


def test_missing_reference_html_fails(tmp_path):
    pattern_dir = write_pattern(tmp_path, write_reference=False)
    write_catalog(tmp_path, [catalog_entry(tmp_path, pattern_dir)])

    result = run_validator(tmp_path)

    assert result.returncode != 0
    assert "reference" in result.stdout.lower() + result.stderr.lower()


def test_valid_minimal_fixture_passes(tmp_path):
    pattern_dir = write_pattern(tmp_path)
    write_catalog(tmp_path, [catalog_entry(tmp_path, pattern_dir)])

    result = run_validator(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("field", "value", "expected_name"),
    [
        ("id", "hero.other", "id"),
        ("family", "summary", "family"),
        ("roles", ["decision"], "roles"),
        ("density", "compact", "density"),
        ("motion", "high", "motion"),
        ("profiles", ["gold"], "profile_affinity"),
    ],
)
def test_catalog_manifest_metadata_drift_names_the_field(tmp_path, field, value, expected_name):
    pattern_dir = write_pattern(tmp_path)
    entry = catalog_entry(tmp_path, pattern_dir)
    entry[field] = value
    write_catalog(tmp_path, [entry])

    result = run_validator(tmp_path)

    output = result.stdout.lower() + result.stderr.lower()
    assert result.returncode != 0
    assert expected_name in output


def test_profile_representation_affinity_must_reference_catalog_id(tmp_path):
    pattern_dir = write_pattern(tmp_path)
    prime_path = tmp_path / "profiles" / "prime.json"
    prime_path.write_text(json.dumps({"id": "prime", "representation_affinity": ["hero.unknown"]}), encoding="utf-8")
    write_catalog(tmp_path, [catalog_entry(tmp_path, pattern_dir)])

    result = run_validator(tmp_path)

    output = result.stdout.lower() + result.stderr.lower()
    assert result.returncode != 0
    assert "representation_affinity" in output
    assert "hero.unknown" in output


def test_pov_corpus_has_exactly_72_patterns_including_wave_e_f_and_g_ids():
    wave_e_ids = {
        "hero.minimal-document",
        "hero.quote-led",
        "hero.metric-led",
        "summary.decision-brief",
        "summary.strategic-thesis",
        "narrative.two-column-editorial",
        "narrative.insight-break",
        "narrative.case-study",
        "decision.recommendation-block",
        "decision.go-no-go",
        "metric.delta-pair",
        "metric.benchmark-bands",
        "comparison.trade-off-matrix",
        "comparison.before-after",
        "financial.investment-case",
    }
    wave_f_ids = {
        "architecture.system-context",
        "architecture.runtime-lifecycle",
        "architecture.dependency-map",
        "architecture.trust-boundary",
        "process.branching-flow",
        "process.state-machine",
        "process.approval-chain",
        "timeline.vertical-chronology",
        "timeline.phase-ribbon",
        "timeline.evolution-ladder",
        "evidence.source-matrix",
        "evidence.confidence-bands",
        "evidence.contradiction-view",
        "risk.risk-matrix",
        "technical.api-exchange",
    }
    wave_g_ids = {
        "operational.runbook",
        "operational.action-queue",
        "operational.shift-handoff",
        "people.raci",
        "people.stakeholder-map",
        "people.decision-ownership",
        "media.screenshot-evidence",
        "media.annotated-image",
        "media.visual-comparison",
        "appendix.sources",
        "appendix.assumptions",
        "appendix.change-log",
        "technical.schema-panel",
        "financial.pricing-matrix",
        "risk.readiness-board",
    }
    manifests = list((ROOT / "library").rglob("manifest.json"))
    manifest_ids = {json.loads(path.read_text(encoding="utf-8"))["id"] for path in manifests}
    entries = [
        json.loads(line)
        for line in (ROOT / "index" / "catalog.ndjson").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    catalog_ids = {entry["id"] for entry in entries}

    assert len(manifests) == 72
    assert len(entries) == 72
    assert len(manifest_ids) == 72
    assert len(catalog_ids) == 72
    assert catalog_ids == manifest_ids
    assert wave_e_ids <= manifest_ids
    assert wave_e_ids <= catalog_ids
    assert wave_f_ids <= manifest_ids
    assert wave_f_ids <= catalog_ids
    assert wave_g_ids <= manifest_ids
    assert wave_g_ids <= catalog_ids


def test_corpus_covers_all_required_representation_families():
    required_families = {
        "hero",
        "summary",
        "metric",
        "comparison",
        "timeline",
        "process",
        "architecture",
        "evidence",
        "risk",
        "decision",
        "narrative",
        "technical",
        "operational",
        "people",
        "financial",
        "media",
        "appendix",
    }
    manifest_families = {
        json.loads(path.read_text(encoding="utf-8"))["family"]
        for path in (ROOT / "library").rglob("manifest.json")
    }

    assert required_families <= manifest_families
