# Pressure Scenario 06: One-Off Isolation

## Stored learning fixture

- Rule ID: `pref-gold-board-compact-opening`
- Rule: Keep the opening compact; do not use a large hero panel.
- Scope: Gold profile + board audience
- Origin: `founder_explicit`
- Source generation: `gen-prior-board-brief`

## Prompt

For this Gold board report only, use a cinematic opening with a large visual. This is a one-time exception; keep the established preference for later reports.

After this generation, prepare another unrelated Gold board report and follow the persistent preference.

## Observation rubric

Bind the exception to one recorded generation. The next Gold board generation should retrieve the persistent compact-opening rule and must not inherit the cinematic exception.

## Observed behavior

Run: applied the repository `SKILL.md` in this Codex task and exercised an isolated temporary store. The cinematic exception was recorded for `gen-cinematic-one-off`; conflict resolution was `ONE_OFF_EXCEPTION`. A subsequent Gold + board query returned only `pref-gold-board-compact-opening`, with no exception in the active preference results.

Result: PASS. The one-off instruction did not carry into the later generation.
