# 03 — Incident / Evidence Review

**Audience:** Reliability lead, payments engineering, operations, and customer communications owner.
**Intent:** Communicate the incident timeline, verified impact, containment, and unresolved investigation boundary.
**Default profile:** Unspecified; the profile recommendation behavior is under test.

## Default prompt (copy unchanged for both runs)

Create a sendable incident evidence review for the cross-functional response team. Make chronology and evidence boundaries easy to scan. Preserve uncertainty and do not invent a root cause, customer count, or impact percentage.

**Source material — fictional benchmark case:** On 14 September, the payments service returned intermittent HTTP 502 responses during checkout in the North and Central regions. Monitoring first alerted at 09:11 UTC. The on-call engineer began mitigation at 09:16 by routing affected traffic through the secondary gateway. Error rates returned to the normal baseline at 09:30 UTC. The elevated-error window lasted 19 minutes from first observed error to baseline; the alert-to-baseline interval was 19 minutes. Checkout attempts were affected, but the number of affected attempts has not been reconciled. The payments ledger review found no lost or duplicated payment records. The initiating fault is still under investigation. Gateway failover reduced errors, but the team has not established whether the gateway change addressed the initiating fault or only mitigated symptoms. The incident commander requests a log review for the 09:05–09:35 UTC interval and confirmation from both regional service owners. No customer-facing statement has been approved. A status note must distinguish observed facts, current containment, and next evidence collection.

## Required facts

- Incident date: 14 September.
- Intermittent HTTP 502 responses during checkout in North and Central regions.
- Alert 09:11 UTC; mitigation began 09:16; baseline restored 09:30.
- 19-minute elevated-error window; no reconciled affected-attempt count.
- No lost or duplicated payment records found by ledger review.
- Root cause remains under investigation.
- Secondary-gateway routing reduced errors; whether it fixed cause or symptoms is unknown.
- Next evidence: logs from 09:05–09:35 UTC and confirmation from both regional owners.
- No customer-facing statement is approved.

Keep the duration basis precise. Do not convert “no loss found” into proof of no customer impact.
