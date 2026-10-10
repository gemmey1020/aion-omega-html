---
name: aion-omega-html
description: Use when creating or revising an AION Omega HTML report, dashboard, briefing, system view, or other structured visual artifact that needs profile-aware composition and responsive review.
---

# AION Omega HTML

Create a clear, evidence-led HTML artifact through a bounded profile and pattern workflow. Use the source repository as the canonical skill and corpus. Normal generation treats the corpus as read-only; do not modify reference patterns, manifests, profile definitions, or indexes while producing a report.

## Choose the visual profile

If the user explicitly names Prime, Gold, Silver, or Cyan, that explicit profile choice skips the recommendation gate. Continue with the selected profile and its rules. Otherwise read `index/profile-summary.json`, recommend one profile in a short explanation tied to audience, purpose, and information shape, then wait for the user's choice before building. Do not silently select a profile or treat Prime as a frozen page template.

After the profile is chosen, read only its selected `profiles/{profile}.json` manifest. Preserve the profile's visual character through hierarchy, spacing, color meaning, and composition. The profile reference is guidance; it does not dictate a fixed layout.

## Retrieve narrowly

Use `tools/search-catalog.py` with the chosen profile and the artifact's information roles to shortlist patterns. Inspect the tiny metadata first, then open only the few relevant manifests and references needed to make a composition decision. Do not enumerate or preload the entire library: avoid broad `find library` or `rg --files library` inventories. Full Master files and encyclopedias must not be preloaded; consult a specific source only when a concrete decision requires it. Treat search as a shortlist, not as an automatic design choice. State briefly why the selected pattern or combination fits the content.

## Compose and build

Choose a composition that follows the information: decision, evidence, comparison, sequence, architecture, or narrative. Combine patterns only when each serves a distinct role. Keep claims, numbers, assumptions, and source boundaries faithful to supplied evidence. Label illustrative or uncertain material. Prefer semantic HTML and CSS. HTML/CSS is the default; use SVG, Canvas, D3, React, or another framework only when it materially improves the information's clarity or interaction.

Build a standalone artifact when the user asks for a self-contained report. Keep the copy readable, accessible, and appropriate for the selected profile. Do not add data, claims, or motion for decoration.

## Review before delivery

Render and inspect desktop and mobile views with `tools/render-preview.mjs`. Check text legibility, hierarchy, clipping, direction, contrast, and horizontal overflow at both sizes. Maximum 2 automatic repairs are allowed. If a defect remains, make at most 2 automatic repair rounds, then render and inspect again. If material defects remain after the second round, report the limitation instead of calling the output complete.

Deliver the artifact path and a concise account of the chosen profile, composition, responsive review, and any unresolved issue. Do not claim visual verification without inspecting both rendered sizes. For PoV work, stop at the Founder verdict; do not begin a later plan without explicit approval.
