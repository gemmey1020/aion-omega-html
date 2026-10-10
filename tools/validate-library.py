#!/usr/bin/env python3
"""Validate AION pattern manifests and their tiny NDJSON catalog."""

import argparse
import json
from pathlib import Path
import sys

REQUIRED_MANIFEST_FIELDS = {
    "id",
    "family",
    "roles",
    "best_for",
    "avoid_when",
    "density",
    "motion",
    "profile_affinity",
    "capabilities",
    "variant_axes",
    "reference",
}
LIST_MANIFEST_FIELDS = {
    "roles",
    "best_for",
    "avoid_when",
    "profile_affinity",
    "capabilities",
    "variant_axes",
}
CATALOG_FIELDS = {
    "id",
    "family",
    "roles",
    "profiles",
    "density",
    "motion",
    "audiences",
    "keywords",
    "manifest",
}


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _read_profile_ids(root: Path, errors: list[str]) -> set[str]:
    profiles_dir = root / "profiles"
    profile_ids = set()
    if not profiles_dir.is_dir():
        errors.append("missing profiles directory: profiles")
        return profile_ids

    for path in sorted(profiles_dir.glob("*.json")):
        try:
            profile = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"malformed profile JSON at {_relative(path, root)}: {exc}")
            continue
        profile_id = profile.get("id") if isinstance(profile, dict) else None
        if not isinstance(profile_id, str) or not profile_id:
            errors.append(f"profile id missing at {_relative(path, root)}")
            continue
        if profile_id in profile_ids:
            errors.append(f"duplicate profile id: {profile_id}")
        profile_ids.add(profile_id)
    return profile_ids


def validate_library(root: Path) -> list[str]:
    """Return validation errors for the library and catalog beneath ``root``."""
    root = Path(root).resolve()
    errors: list[str] = []
    profile_ids = _read_profile_ids(root, errors)
    library_dir = root / "library"
    if not library_dir.is_dir():
        errors.append("missing library directory: library")
        manifests = []
    else:
        manifests = sorted(library_dir.rglob("manifest.json"))

    by_path: dict[Path, dict] = {}
    by_id: dict[str, Path] = {}
    for path in manifests:
        relative = _relative(path, root)
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"malformed manifest JSON at {relative}: {exc}")
            continue
        if not isinstance(manifest, dict):
            errors.append(f"manifest must be a JSON object at {relative}")
            continue

        missing = REQUIRED_MANIFEST_FIELDS - manifest.keys()
        if missing:
            errors.append(f"missing manifest fields at {relative}: {', '.join(sorted(missing))}")
        for field in LIST_MANIFEST_FIELDS:
            if field in manifest and not isinstance(manifest[field], list):
                errors.append(f"manifest field {field} must be a list at {relative}")
        pattern_id = manifest.get("id")
        if isinstance(pattern_id, str) and pattern_id:
            if pattern_id in by_id:
                errors.append(f"duplicate id: {pattern_id} in {_relative(by_id[pattern_id], root)} and {relative}")
            else:
                by_id[pattern_id] = path
        for profile_id in manifest.get("profile_affinity", []) if isinstance(manifest.get("profile_affinity", []), list) else []:
            if profile_id not in profile_ids:
                errors.append(f"invalid profile {profile_id!r} in {relative}")

        reference = manifest.get("reference")
        if isinstance(reference, str) and reference:
            reference_path = (path.parent / reference).resolve()
            if not reference_path.is_relative_to(path.parent.resolve()):
                errors.append(f"reference escapes pattern directory at {relative}: {reference}")
            elif not reference_path.is_file():
                errors.append(f"missing reference HTML at {_relative(reference_path, root)} (from {relative})")
        by_path[path.resolve()] = manifest

    catalog_path = root / "index" / "catalog.ndjson"
    if not catalog_path.is_file():
        errors.append("missing catalog: index/catalog.ndjson")
        return errors

    seen_catalog_ids: set[str] = set()
    seen_manifest_paths: set[Path] = set()
    try:
        catalog_lines = catalog_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return errors + [f"cannot read catalog index/catalog.ndjson: {exc}"]

    for line_number, line in enumerate(catalog_lines, 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"malformed catalog JSON at index/catalog.ndjson:{line_number}: {exc}")
            continue
        if not isinstance(entry, dict):
            errors.append(f"catalog entry must be an object at index/catalog.ndjson:{line_number}")
            continue
        missing = CATALOG_FIELDS - entry.keys()
        if missing:
            errors.append(f"missing catalog fields at index/catalog.ndjson:{line_number}: {', '.join(sorted(missing))}")
        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            if entry_id in seen_catalog_ids:
                errors.append(f"duplicate catalog id: {entry_id}")
            seen_catalog_ids.add(entry_id)
        for profile_id in entry.get("profiles", []) if isinstance(entry.get("profiles", []), list) else []:
            if profile_id not in profile_ids:
                errors.append(f"invalid profile {profile_id!r} in catalog entry {entry_id!r}")

        manifest_ref = entry.get("manifest")
        if not isinstance(manifest_ref, str) or not manifest_ref:
            continue
        manifest_path = (root / manifest_ref).resolve()
        if not manifest_path.is_relative_to(root) or manifest_path not in by_path:
            errors.append(f"catalog entry points to missing pattern: {manifest_ref}")
            continue
        seen_manifest_paths.add(manifest_path)
        manifest = by_path[manifest_path]
        if entry_id != manifest.get("id"):
            errors.append(
                f"catalog id {entry_id!r} does not match manifest id {manifest.get('id')!r} at {_relative(manifest_path, root)}"
            )

    for path in by_path:
        if path not in seen_manifest_paths:
            errors.append(f"manifest not indexed in catalog: {_relative(path, root)}")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="AION source root (default: current directory)")
    args = parser.parse_args(argv)

    errors = validate_library(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    count = len(list((args.root / "library").rglob("manifest.json")))
    print(f"Library valid: {count} pattern(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
