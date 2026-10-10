# Scenario 01 — Explicit Scoped Correction Carries Forward

**Goal:** Prove that an explicit Founder preference applies to the next matching generation without spreading to unrelated contexts.

## Fixture

- Generation ID: gen-prime-strategy-01
- Scope: profile Prime, audience founder-strategy, artifact type strategy memo, project Plan2-demo
- Founder correction: “For Prime founder strategy memos in this project, leave more open editorial space and reduce panel density.”
- Target: composition density

## Procedure

Record the generation and explicit correction; check for conflicts before activation; activate only if no overlapping rule exists. Query the same scope and a different audience/profile.

## Expected

The matching query returns the active rule with source generation and Founder origin. A board decision or Silver audit query does not receive this scoped rule. No files in profiles/, library/, or canon are changed.
