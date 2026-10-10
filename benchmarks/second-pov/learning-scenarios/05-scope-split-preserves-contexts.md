# Scenario 05 — Scope Split Preserves Two Contexts

**Goal:** Prove that a broad rule can be replaced by two distinct, narrower Founder rules without losing either context.

## Fixture

- Existing rule: Prime uses an open editorial opening; scope is profile Prime.
- New explicit correction conflicts with the broad rule.
- Test-only simulated resolution supplied by this fixture: SCOPE_SPLIT.
- Replacement A: open, narrative opening for Prime founder-strategy memos.
- Replacement B: concise, decision-first opening for Prime board decision briefs.

## Procedure

Record the conflict and apply the fixture’s two strictly narrower split rules. Query founder-strategy, board-decision, and unrelated client-proposal contexts.

## Expected

The original broad rule is preserved as superseded, with both new rules linked through supersedes. The strategy query returns only the strategy rule; the board query returns only the board rule; the unrelated client query receives neither. The simulated resolution is test data, not a Founder decision.
