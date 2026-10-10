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
    include_borrowed: bool = False,
    borrow_limit: int = 3,
) -> list[dict]:
    """Return ranked catalog records; this helper does not select a design."""
    if limit < 0:
        raise ValueError("limit must be zero or greater")
    if borrow_limit < 0:
        raise ValueError("borrow_limit must be zero or greater")
    requested_profiles = _terms(profiles)
    requested_roles = _terms(roles)
    requested_audiences = _terms(audiences)
    requested_keywords = _terms(keywords)
    has_semantic_query = bool(requested_roles or requested_audiences or requested_keywords)

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

    native_ranked = []
    borrowed_ranked = []
    for row in rows:
        row_profiles = _terms(row.get("profiles", []))
        profile_match = bool(requested_profiles & row_profiles)
        if requested_profiles and not profile_match and not include_borrowed:
            continue

        role_matches = requested_roles & _terms(row.get("roles", []))
        audience_matches = requested_audiences & _terms(row.get("audiences", []))
        keyword_matches = requested_keywords & _terms(row.get("keywords", []))
        semantic_score = 4 * len(role_matches)
        semantic_score += 2 * len(audience_matches)
        semantic_score += len(keyword_matches)
        if has_semantic_query and semantic_score == 0:
            continue

        match_scope = "native" if not requested_profiles or profile_match else "borrowed"
        score = semantic_score + (3 if profile_match else 0)
        result = dict(
            row,
            score=score,
            semantic_score=semantic_score,
            match_scope=match_scope,
        )
        ranked_row = (score, str(row.get("id", "")), result)
        if match_scope == "native":
            native_ranked.append(ranked_row)
        else:
            borrowed_ranked.append(ranked_row)

    sort_key = lambda item: (-item[0], item[1])
    native_ranked.sort(key=sort_key)
    borrowed_ranked.sort(key=sort_key)
    native_results = [row for _, _, row in native_ranked]
    if requested_profiles and include_borrowed:
        borrowed_results = [row for _, _, row in borrowed_ranked[:borrow_limit]]
    else:
        borrowed_results = []
    return (native_results + borrowed_results)[:limit]


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
    parser.add_argument("--include-borrowed", action="store_true")
    parser.add_argument("--borrow-limit", type=int, default=3)
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be zero or greater")
    if args.borrow_limit < 0:
        parser.error("--borrow-limit must be zero or greater")
    try:
        results = search_catalog(
            args.catalog,
            profiles=_csv(args.profile),
            roles=_csv(args.roles),
            audiences=_csv(args.audiences),
            keywords=_csv(args.keywords),
            limit=args.limit,
            include_borrowed=args.include_borrowed,
            borrow_limit=args.borrow_limit,
        )
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
