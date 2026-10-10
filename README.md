# AION Omega HTML

Source repository for the AION Omega HTML Codex skill, profile contracts, reference corpus, and preview tooling. The source repository is canonical; `~/.agents/skills/aion-omega-html/` is a discoverable copy used for Task 10 pressure testing.

## Prerequisites

- Python 3.11 or newer
- Node.js and npm
- `uv` for the repository's isolated pytest command
- Playwright Chromium for reference rendering; install the pinned Node dependency from this repository

```bash
npm install
npx playwright install chromium
```

## Validate and test locally

Run the mechanical suite and library validator from the repository root:

```bash
uv run --no-project --with pytest pytest -q
python3 tools/validate-library.py --root .
```

## Render a reference

The renderer writes a 1440px desktop and 390px mobile PNG:

```bash
node tools/render-preview.mjs \
  --input library/hero/compact-document/reference.html \
  --desktop /tmp/aion-desktop.png \
  --mobile /tmp/aion-mobile.png
```

Inspect both images before accepting a visual change. Keep reference pages responsive and self-contained.

## PoV boundary

Plan 1 ends at the Task 12 Founder verdict. Stop there and present the evidence with one verdict candidate: PASS, CORRECT, or KILL. Do not begin Plan 2 without explicit Founder approval.
