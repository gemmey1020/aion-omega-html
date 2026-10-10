# Early PoV Benchmark Runbook

This harness compares clean Codex with AION on six realistic cases. The only intended treatment difference is whether the AION skill is available and explicitly loaded. The prompts in `cases/` contain the source, audience, intent, and objective; keep each prompt byte-for-byte identical across its pair. No default prompt specifies a visual profile, so the profile recommendation gate is measured.

## Controlled run procedure

1. Use a fresh Codex process for every artifact. Use the same model class and reasoning setting within a pair; default to `gpt-6-luna` at low effort. No subagents. Do not use Sol by default.
2. Give the clean run the case's default prompt and the same read-only source inputs available to AION, but make the AION skill unavailable. State that no installed skill or custom workflow should be loaded. Inspect the run log to confirm no skill file was read.
3. Give the AION run the exact same default prompt, then add only the instruction to read and follow the source skill `SKILL.md`. Keep the same source facts, audience, output location rules, model class, and reasoning setting.
4. Allow one initial generation and at most two correction rounds for each side. Keep every correction request and budget equivalent. Do not provide a profile name or profile semantics in either default prompt. If a user explicitly selects a profile in a separate profile-differentiation experiment, record that separately.
5. Save each resulting standalone HTML, desktop PNG, mobile PNG, and run log under a case-specific results directory. Inspect desktop and mobile; record any overflow, clipping, bidi issue, illegible diagram, or missing fact. A missing render is a missing evaluation artifact, not a pass.
6. For AION, record every profile, catalog, manifest, and reference file actually read during retrieval. Count distinct files, not tool calls. A broad corpus listing or loading all masters/examples is a retrieval failure.
7. Before Founder judging, assign random A/B labels, keep the mapping in a separate sealed key, and remove profile names, generator labels, filenames, and obvious metadata from the artifacts where feasible. Present the same source facts and judging question for both.
8. Preserve the source prompt, raw logs, HTML, screenshots, scorecard, and blind key. Do not overwrite a failed run; label reruns and retain the previous evidence.

## Case index

| ID | Case | Main decision or reading challenge |
|---|---|---|
| 01 | Executive decision | Launch timing, contractual pressure, operational control, bounded recommendation |
| 02 | Founder strategy | Growth focus, mixed Arabic-English source, evidence versus hypothesis |
| 03 | Incident evidence | Chronology, impact boundary, containment versus unknown cause |
| 04 | Architecture | Proposed versus current state, trust boundaries, failure and replay questions |
| 05 | Operations status | Counts, blockers, owners, due dates, mixed Arabic-English source |
| 06 | Client commercial | Pilot scope, fee, assumptions, acceptance, exclusions, open start date |

## Founder verdict boundary

Task 12 ends with one evidence-backed verdict candidate: PASS, CORRECT, or KILL. Stop after presenting the evidence and candidate. Do not start Plan 2 until the Founder explicitly approves it.
