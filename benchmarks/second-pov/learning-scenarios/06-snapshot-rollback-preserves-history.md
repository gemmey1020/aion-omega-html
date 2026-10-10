# Scenario 06 — Snapshot Rollback Restores Derived State and Preserves History

**Goal:** Prove that rollback restores derived learning state without deleting append-only events or touching product authorities.

## Fixture

- Initial active rule and candidate are recorded.
- Create a snapshot of derived state.
- Add a later rule, candidate, and conflict.
- Preserve byte fingerprints of profiles/, library/, and canon/ before the rollback.

## Procedure

Restore the snapshot, compare all derived learning state, event history, and protected file fingerprints.

## Expected

Active rules, candidates, conflicts, and superseded state match the snapshot. Existing event lines remain byte-identical and a new rollback event is appended. profiles/, library/, and canon/ are unchanged; the snapshot remains available.
