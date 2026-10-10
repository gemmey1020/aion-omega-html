# Retrieval record — 04-architecture

- Recommended profile: **Cyan**
- Selected profile: **Cyan**
- Catalog query: `profile=cyan; roles=architecture,sequence,evidence; keywords="event intake resolver trust boundary review"; limit=12`
- Candidate shortlist limit: **12** manifests; no full-corpus preload
- Profile manifest: `profiles/cyan.json`
- Shortlist metadata: `index/profile-summary.json`, `index/catalog.ndjson`
- Pattern manifests opened: **5**
- `library/architecture/data-flow`
- `library/architecture/layered`
- `library/architecture/control-plane`
- `library/evidence/evidence-ledger`
- `library/process/linear-pipeline`
- Implementation references opened: **4**
- `library/architecture/data-flow/reference.html`
- `library/architecture/control-plane/reference.html`
- `library/process/linear-pipeline/reference.html`
- `library/architecture/layered/reference.html`
- Complete examples opened: **0**
- Capability choice: **HTML/CSS**; native document structure and CSS layout, no SVG/Canvas/React/Astro/D3.
- Automatic repair rounds: **1**
- Distinct retrieval corpus files counted: **12** (profile + shortlist + opened manifests, references, and any complete example; excludes the skill, source case, and tool documentation).
- Read-set receipt: the exact profile/catalog/manifest/reference paths opened for retrieval are listed below.

- `profiles/cyan.json`
- `index/profile-summary.json`
- `index/catalog.ndjson`
- `library/architecture/data-flow/manifest.json`
- `library/architecture/layered/manifest.json`
- `library/architecture/control-plane/manifest.json`
- `library/evidence/evidence-ledger/manifest.json`
- `library/process/linear-pipeline/manifest.json`
- `library/architecture/data-flow/reference.html`
- `library/architecture/control-plane/reference.html`
- `library/process/linear-pipeline/reference.html`
- `library/architecture/layered/reference.html`

## Notes

The first keyword argument form returned no usable shortlist; the quoted phrase form above succeeded. One repair round corrected arrow direction, removed internal retrieval/profile metadata from the client-facing artifact, and stacked the mobile table. No complete example was opened.
