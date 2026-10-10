# Pressure Scenario 04: Learning Carryover

## Stored learning fixture

- Rule ID: `pref-gold-board-compact-opening`
- Rule: Keep the opening compact; do not use a large hero panel.
- Scope: Gold profile + board audience
- Origin: `founder_explicit`
- Source generation: `gen-prior-board-brief`

## Prompt

Create a Gold decision brief for the board about whether to delay a product launch after reliability testing found intermittent failures. Use the established opening preference and keep the recommendation and trade-off easy to scan.

## Observation rubric

After Gold is selected, query only matching learning. Apply the compact opening preference and retain its scope and provenance. Do not widen it to other profiles or audiences.

## Observed behavior

Run: applied the repository `SKILL.md` in this Codex task and verified the query against an isolated temporary learning store. The selected Gold + board scope returned `pref-gold-board-compact-opening`; its scope, `founder_explicit` origin, and `gen-prior-board-brief` provenance were preserved. No unrelated profile rule was returned.

Result: PASS. This checks learning selection and carryover; it does not claim an HTML artifact render.
