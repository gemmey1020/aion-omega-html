# AION Omega HTML

A work-in-progress Codex skill and reference toolkit for building clear, evidence-led HTML reports. The project combines report profiles, reusable layout patterns, a searchable example library, validation tools, and desktop/mobile preview rendering.

This is an independent prototype, not an official Codex feature or a production release.

## Repository layout

- `SKILL.md` — skill entrypoint and operating guidance.
- `profiles/` — report profile contracts and composition rules.
- `library/` — reusable HTML patterns and their manifests.
- `knowledge/` and `index/` — reference material and catalog data.
- `examples/` — profile examples.
- `tools/` — catalog search, library validation, and preview rendering.
- `benchmarks/` and `tests/` — example cases and quality checks.

## Setup

Requirements: Python 3.11+, Node.js, npm, and `uv`.

```bash
npm install
npx playwright install chromium
```

## Useful commands

Validate the pattern library:

```bash
python3 tools/validate-library.py --root .
```

Run the test suite:

```bash
uv run --no-project --with pytest pytest -q
```

Render a reference pattern for desktop and mobile review:

```bash
node tools/render-preview.mjs \
  --input library/hero/compact-document/reference.html \
  --desktop /tmp/aion-desktop.png \
  --mobile /tmp/aion-mobile.png
```

Review both rendered sizes before accepting a visual change. Benchmark examples are demonstrations; inspect their content before reusing them in client work.

## Branches

- `main` — the later second proof-of-value work.
- `codex/aion-omega-html-early-pov` — the earlier proof-of-value work.

## Data and licensing

User-specific learning records and the Founder-approved seed reference are intentionally excluded from this public repository. Do not add personal, client, or credential data to benchmark files.

No license is included. Public visibility does not grant reuse rights; contact the rights holder before redistributing or adapting this work.
