# 04 — Architecture Report

**Audience:** Engineering leadership, platform engineers, security reviewer, and service owners.
**Intent:** Explain a proposed event-driven intake and review architecture, its trust boundaries, failure behavior, and decision points.
**Default profile:** Unspecified; the profile recommendation behavior is under test.

## Default prompt (copy unchanged for both runs)

Create an architecture review document that explains the proposed system and surfaces the most important failure and ownership boundaries. A diagram is welcome only if it makes the flow easier to understand. Distinguish current components from proposed ones. Do not claim that the proposed controls are already deployed.

**Source material — fictional benchmark case:** The current service accepts a partner webhook, writes the raw payload to an intake queue, normalizes the event, and posts an update to an operations dashboard. The proposal adds an evidence resolver between normalization and the dashboard. Each normalized event carries an event ID, partner ID, received time, and source URL when available. The resolver checks URL reachability and records a content hash, retrieval time, and resolver status. It must not silently replace the partner's source URL. A policy service decides whether an event is eligible for automated posting. Events with missing, unreachable, or changed sources are held for human review; they must not be labeled verified. The dashboard reads only the normalized event and review status, not the raw webhook secret. Queue retries currently use exponential backoff up to six attempts, after which the event enters a dead-letter queue. There is no confirmed replay UI or idempotency guarantee for the proposed resolver. The security reviewer asks how secrets are kept out of logs, how an operator can correct a false hold, and whether a replay can produce duplicate dashboard updates. The engineering team has not selected a database or deployment topology. The system must remain auditable by event ID from receipt through final status.

## Required facts

- Current flow: webhook → raw intake queue → normalization → operations dashboard.
- Proposed evidence resolver sits after normalization and before dashboard publication.
- Event fields: event ID, partner ID, received time, optional source URL.
- Resolver metadata: reachability, content hash, retrieval time, status; original URL remains unchanged.
- Missing, unreachable, or changed source means hold for human review, never “verified.”
- Dashboard sees normalized event and review status, not raw webhook secret.
- Current retry policy: exponential backoff up to six attempts, then dead-letter queue.
- Replay UI and resolver idempotency are unresolved; duplicate update risk is an open question.
- Database and deployment topology are not selected.
- Audit trail must follow event ID from receipt through final status.

Show trust boundaries, ownership, and unresolved design questions without presenting proposed controls as existing production behavior.
