# 04 — System Architecture: Offline Tree Survey

**Audience:** Municipal tree-survey stewards, mobile engineers, records owners, and the privacy reviewer.
**Purpose:** Explain a proposed offline-first field-survey system, its data path, trust boundaries, failure behavior, and open design decisions.
**Required output language:** Arabic.
**Artifact:** An architecture review in Arabic that distinguishes the current process from the proposal.

## Source facts

- Surveyors currently record urban tree inspections on paper; a records clerk later enters them into the municipal asset register.
- Twelve surveyors are assigned to the seasonal inspection program.
- The proposal introduces a tablet app that can hold draft inspections while a surveyor is offline.
- Each inspection contains a stable survey ID, street-segment ID, observation time, condition code, and optional photo.
- A sync gateway is proposed to validate the app version and required fields before sending a record to the steward review console.
- Duplicate survey IDs and conflicting edits must be held for steward review; the system must not silently replace an existing register entry.
- The public map may display an approved condition summary, but must not expose staff route history or photo metadata.
- An asset-register interface will remain the source of truth for accepted records.

## Unknowns and assumptions boundary

- Local-device encryption and retention periods have not been approved.
- The conflict rule for a survey edited on two tablets is undecided.
- No decision has been made about the duration of offline drafts.
- The approved purpose and retention period for optional photos are unknown.
- The design is proposed; none of the proposed controls should be described as deployed.

## Default task

أنشئ مراجعة معمارية توضّح المسار المقترح وحدود الثقة ومسؤولية المراجعة وسلوك فشل المزامنة. افصل العملية الحالية عن التصميم المقترح، واعرض الأسئلة المفتوحة دون ادعاء أن الضوابط المقترحة منشورة.
