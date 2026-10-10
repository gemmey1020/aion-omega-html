# AION Plan 2 — Second PoV

**Status:** harness ready; evaluation outputs and Founder judgments are not populated.
**Product:** aion-omega-html, Plan 2, 72-pattern corpus.
**Execution posture:** Luna-class, no subagents, narrow retrieval, at most two repair rounds.

## Purpose

Compare six fresh AION artifacts against clean intelligent generation using the same model class, source facts, audience, purpose, and required language. This tests practical value, profile selection, retrieval breadth, artifact quality, and the learning contract. Plan 1 facts are not reused.

The cases are fictional benchmark material. Each case file is the factual boundary. The six required output languages are fixed before generation and are identical for both sides:

| Case | Audience / purpose | Required output language |
|---|---|---|
| 01 — Board decision | Museum trustees; choose a bounded public-release path | English |
| 02 — Founder strategy | Independent publisher founder; choose next-season focus | Arabic |
| 03 — Incident audit | Records integrity and platform team; report evidence and next checks | English |
| 04 — System architecture | Municipal tree-survey stewards and engineers; explain a proposed offline system | Arabic |
| 05 — Operations handoff | Forum operations lead; transfer event setup state and next actions | English |
| 06 — Client proposal | Cultural-trust finance and communications leads; decide on a bounded accessibility project | Arabic |

## Isolation contract

For every case, start from a fresh, empty generation workspace and a fresh model session.

- Clean receives exactly the case file and its clean prompt. Do not install, expose, call, or reference any AION skill, profile, pattern library, retrieval index, learning store, or AION output.
- AION receives exactly the same case and its AION prompt, plus the installed aion-omega-html skill discoverable through the normal skill mechanism. Its profile/library/canon remain read-only; agent inference remains candidate-only.
- Never put the counterpart output, screenshot, retrieval notes, scorecard, or A/B mapping in either generation workspace.
- Keep each run isolated from the other five runs. Capture the model/runtime identity and available settings before generation.
- After generation, save the artifact and its run record outside the active generation workspace. Render and inspect only after both sides are sealed.
- If a genuinely skill-free clean session cannot be proven, stop before generating any clean artifact. Record the missing isolation evidence and request the smallest Founder action needed. Do not simulate clean output from an AION-loaded session.

The AION run record must preserve selected or recommended profile, retrieved rows, manifests/references/examples actually opened, learning entries loaded, capabilities used, repair rounds, and QA receipt paths. Do not claim a file or learning entry was read unless its access is recorded.

## Blind A/B protocol

The answer key is precommitted in results/ab-mapping.json and must not be copied into scorecards, artifact names, screenshots, or review packets. Every scorecard uses only A and B. Keep the answer key away from the Founder until all six blinded judgments are recorded. The assignment contains exactly three cases with AION as A and three with AION as B.

The paired artifacts must use the same case facts and fixed language. Render both at desktop and mobile. Do not edit either artifact after its A/B label is assigned. If a repair is needed before blinding, record it and regenerate that artifact's QA receipts first.

## Scoring

Use results/scorecard-template.md. Score content fidelity, visual hierarchy, readability, representation quality, professional sendability, and overall usefulness from 1 to 5 with an evidence note. Founder-only fields remain blank until Founder review. A mechanical or Codex review note is not a Founder judgment.

A critical content failure includes an invented or contradicted material fact; omission that changes the decision; an unsupported claim of approval, deployment, safety, customer impact, price, or completion; or violating the fixed output language. Describe evidence for any failure.

## Second-PoV gates

All gates must be satisfied for a PASS candidate:

- zero critical AION content failures across six cases
- Founder WOULD_SEND = YES for at least 5 of 6 AION artifacts
- AION wins or ties clean in at least 4 of 6 blinded pairs
- mean AION quality score is at least the clean mean
- all four profiles are materially distinct in the same-source blind set, including structure and rhythm rather than color alone
- all six learning scenarios behave as specified
- retrieval is narrow and no full-corpus preload occurs
- a routine artifact completes within at most two repair rounds

A missing Founder score is UNKNOWN, not a pass. The candidate verdict may be PASS, CORRECT, or KILL, but only the Founder fills the Founder verdict and judgment fields.

## Learning behavior

The six scenarios under learning-scenarios/ are local fixtures. Scenarios 4 and 5 explicitly provide simulated resolution choices for mechanical continuation; those are test inputs, not Founder decisions. Scenario 3 stops at the unresolved conflict gate and presents exactly KEEP OLD / OVERRIDE / SCOPE SPLIT / ONE-OFF EXCEPTION. No resolution is inferred.

## Same-source profile distinction

cases/profile-distinction-source.md is a separate fixture, not one of the six A/B cases. Generate four isolated variants from the identical source, audience, purpose, and language, assigning Prime, Gold, Silver, and Cyan explicitly. Blind the labels before review using the same score dimensions. Keep the profile key outside the Founder packet until judgment is recorded.
