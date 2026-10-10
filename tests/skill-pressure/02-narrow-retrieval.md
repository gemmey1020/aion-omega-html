# Pressure Scenario 02: Narrow Retrieval

## Clean-session prompt

You have a local reference library at `references/` containing 80 standalone HTML reports with different visual patterns and a `catalog.ndjson` file with short metadata for each report. Create a polished, sendable incident report from this source:

> A payment service returned intermittent 502 errors for 19 minutes. The alert fired at 09:11 UTC, mitigation began at 09:16, and error rates returned to baseline at 09:30. The root cause is still under investigation. No payment records were lost. The incident affected checkout attempts in two regions.

Use the reference library if useful. Tell me which files you inspected and why before presenting the report.

## Observation rubric

Record whether the agent starts from the small catalog and narrows to a few candidates, or opens/reads a broad slice of the 80 references before shortlisting. Do not tell the agent to use a specific retrieval procedure.
