#!/usr/bin/env python3
"""Mechanically shortlist AION patterns from the tiny NDJSON catalog."""

import argparse
import json
from pathlib import Path
import sys
from typing import Iterable


def _terms(values: Iterable[str] | str | None) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        values = values.split(",")
    return {value.strip().casefold() for value in values if value.strip()}


def search_catalog(
    catalog_path: Path | str,
    profiles: Iterable[str] | str | None = None,
    roles: Iterable[str] | str | None = None,
    audiences: Iterable[str] | str | None = None,
    keywords: Iterable[str] | str | None = None,
    limit: int = 12,
) -> list[dict]:
    """Return ranked catalog records; this helper does not select a design."""
    if limit < 0:
        raise ValueError("limit must be zero or greater")
    requested_profiles = _terms(profiles)
    requested_roles = _terms(roles)
    requested_audiences = _terms(audiences)
    requested_keywords = _terms(keywords)

    rows = []
    path = Path(catalog_path)
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed catalog JSON at {path}:{line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"catalog entry must be an object at {path}:{line_number}")
        rows.append(row)

    ranked = []
    for row in rows:
        row_profiles = _terms(row.get("profiles", []))
        profile_match = bool(requested_profiles & row_profiles)
        if requested_profiles and not profile_match:
            continue

        role_matches = requested_roles & _terms(row.get("roles", []))
        audience_matches = requested_audiences & _terms(row.get("audiences", []))
        keyword_matches = requested_keywords & _terms(row.get("keywords", []))
        score = 4 * len(role_matches)
        score += 3 if profile_match else 0
        score += 2 * len(audience_matches)
        score += len(keyword_matches)
        ranked.append((score, str(row.get("id", "")), row))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [dict(row, score=score) for score, _, row in ranked[:limit]]


def _csv(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--profile", help="Requested profile ID")
    parser.add_argument("--roles", help="Comma-separated information roles")
    parser.add_argument("--audiences", help="Comma-separated audience labels")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be zero or greater")
    try:
        results = search_catalog(
            args.catalog,
            profiles=_csv(args.profile),
            roles=_csv(args.roles),
            audiences=_csv(args.audiences),
            keywords=_csv(args.keywords),
            limit=args.limit,
        )
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
