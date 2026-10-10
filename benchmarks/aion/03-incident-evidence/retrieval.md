# Retrieval record — 03-incident-evidence

- Recommended profile: **Silver**
- Selected profile: **Silver**
- Catalog query: `profile=silver; roles=evidence,timeline,incident; audience=cross-functional; keywords=incident,chronology,containment,uncertainty; limit=8`
- Candidate shortlist limit: **8** manifests; no full-corpus preload
- Profile manifest: `profiles/silver.json`
- Shortlist metadata: `index/profile-summary.json`, `index/catalog.ndjson`
- Pattern manifests opened: **3**
- `library/timeline/incident-sequence`
- `library/evidence/evidence-ledger`
- `library/evidence/claim-proof`
- Implementation references opened: **3**
- `library/timeline/incident-sequence/reference.html`
- `library/evidence/evidence-ledger/reference.html`
- `library/evidence/claim-proof/reference.html`
- Complete examples opened: **0**
- Capability choice: **HTML/CSS**; native document structure and CSS layout, no SVG/Canvas/React/Astro/D3.
- Automatic repair rounds: **0**
- Distinct retrieval corpus files counted: **9** (profile + shortlist + opened manifests, references, and any complete example; excludes the skill, source case, and tool documentation).
- Read-set receipt: the exact profile/catalog/manifest/reference paths opened for retrieval are listed below.

- `profiles/silver.json`
- `index/profile-summary.json`
- `index/catalog.ndjson`
- `library/timeline/incident-sequence/manifest.json`
- `library/evidence/evidence-ledger/manifest.json`
- `library/evidence/claim-proof/manifest.json`
- `library/timeline/incident-sequence/reference.html`
- `library/evidence/evidence-ledger/reference.html`
- `library/evidence/claim-proof/reference.html`

## Notes

Initial audience argument included unquoted spaces and was rejected by the CLI. The corrected query above succeeded. No complete example was opened.
