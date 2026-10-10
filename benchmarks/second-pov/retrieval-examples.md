# AION Retrieval Examples — Plan 2 Task 3

Snapshot from the validated 27-pattern catalog before corpus Wave E. These are direct CLI results; scores are deterministic metadata, not design decisions.

## Native-only profile queries

| Query | CLI criteria | Returned candidates (semantic score; total score) |
|---|---|---|
| Prime — founder strategy | `--profile prime --roles narrative --audiences founder --keywords context --limit 3` | `narrative.long-form-chapter` (7; 10); `architecture.data-flow` (2; 5); `comparison.side-by-side` (2; 5) |
| Gold — external client proposal | `--profile gold --roles option evaluation --audiences client --keywords tradeoff --limit 3` | `comparison.side-by-side` (7; 10); `hero.editorial-split` (2; 5); `narrative.long-form-chapter` (2; 5) |
| Silver — audit evidence | `--profile silver --roles evidence --audiences technical --keywords source --limit 3` | `evidence.claim-proof` (7; 10); `timeline.evidence-timeline` (7; 10); `evidence.evidence-ledger` (6; 9) |
| Cyan — architecture runtime | `--profile cyan --roles architecture --audiences engineering --keywords runtime --limit 3` | `architecture.control-plane` (7; 10); `architecture.data-flow` (6; 9); `architecture.layered` (6; 9) |

## Explicit controlled borrowing

| Query | CLI criteria | Returned borrowed candidates (semantic score; total score) |
|---|---|---|
| Gold — architecture borrowing | `--profile gold --roles architecture --audiences engineering --keywords runtime --include-borrowed --borrow-limit 2 --limit 3` | `architecture.control-plane` (7; 7); `architecture.data-flow` (6; 6) |

The Gold query asks for architecture/runtime information. No native Gold architecture row matches this query, so the explicitly enabled search returns the relevant Cyan/Silver architecture rows as `borrowed`, capped at two. Profile affinity does not contribute to `semantic_score`; with any semantic query present, a row needs at least one role, audience, or keyword match.
