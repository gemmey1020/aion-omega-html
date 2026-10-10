# Scenario 02 — Agent Inference Remains Candidate-Only

**Goal:** Prove that a preference inferred from output behavior does not become an active Founder rule.

## Fixture

- Observation: the generated brief used a dense opening panel twice.
- Inference candidate: “The Founder may prefer a more open opening.”
- Origin: agent_inference
- Scope: profile Gold, audience board

## Procedure

Add the inference as a candidate, then query active rules for the same scope. Attempting to activate the inference directly must be rejected.

## Expected

The candidate is present with candidate status and agent_inference provenance. No matching active preference is created. The event history records candidate addition; it does not record Founder approval.
