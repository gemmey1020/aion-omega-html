# Scenario 04 — One-Off Exception Does Not Leak

**Goal:** Confirm that a one-generation exception leaves the active rule intact and does not affect later matching generations.

## Fixture

- Active rule: Gold board briefs use a restrained, low-density opening.
- Recorded generation: gen-gold-board-once.
- Test-only simulated resolution supplied by this fixture: ONE_OFF_EXCEPTION for this generation only.
- Exception: use an image-led opening for gen-gold-board-once.

## Procedure

Record the generation, create the direct conflict against the active rule, and apply only the fixture’s simulated exception choice. Query a later Gold board brief without passing the one-off exception.

## Expected

The exception is generation_only and tied to gen-gold-board-once. The original active rule remains queryable for later generations. The simulated choice is test data, not a Founder decision.
