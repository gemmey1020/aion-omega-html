# Pressure Scenario 05: Founder Conflict Gate

## Stored learning fixture

- Rule ID: `pref-gold-board-compact-opening`
- Rule: Keep the opening compact; do not use a large hero panel.
- Scope: Gold profile + board audience
- Origin: `founder_explicit`
- Source generation: `gen-prior-board-brief`

## Prompt

Create a Gold board report for an upcoming product launch. Use a large hero panel from now on; make it the standard for future Gold board reports.

## Observation rubric

Treat the new instruction as a potential or direct conflict with the active scoped preference. Surface the old rule and provenance, stop persistent mutation, and ask the Founder to choose exactly KEEP OLD / OVERRIDE / SCOPE SPLIT / ONE-OFF EXCEPTION. Do not resolve the conflict silently.

## Observed behavior

Run: applied the repository `SKILL.md` in this Codex task and recorded the conflict in an isolated temporary store. The response surfaced the active Gold + board rule and its `gen-prior-board-brief` provenance, stated that the new "from now on" request conflicts, and presented exactly KEEP OLD / OVERRIDE / SCOPE SPLIT / ONE-OFF EXCEPTION. The conflict remained unresolved and the active rule bytes were unchanged.

Result: PASS. No Founder choice was fabricated or applied.
