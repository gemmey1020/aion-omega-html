import json
import subprocess
import sys
from pathlib import Path

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


def test_pov_corpus_has_exactly_27_unique_patterns():
    manifests = list((ROOT / "library").rglob("manifest.json"))
    entries = [
        json.loads(line)
        for line in (ROOT / "index" / "catalog.ndjson").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(manifests) == 27
    assert len(entries) == 27
    assert len({json.loads(path.read_text(encoding="utf-8"))["id"] for path in manifests}) == 27
    assert len({entry["id"] for entry in entries}) == 27
