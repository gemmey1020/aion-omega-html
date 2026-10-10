---
name: aion-omega-html
description: Use when creating or revising an AION Omega HTML report, dashboard, briefing, system view, or other structured visual artifact that needs profile-aware composition and responsive review.
---

# AION Omega HTML

Create an evidence-led HTML artifact through a bounded profile and pattern workflow. Treat this repository as the canonical skill and corpus. Normal generation treats the corpus as read-only; do not modify reference patterns, manifests, profiles, indexes, or canon while producing a report.

## Choose the visual profile

If the user explicitly names Prime, Gold, Silver, or Cyan, that explicit profile choice skips the recommendation gate. Otherwise read `index/profile-summary.json`, recommend one profile based on audience, purpose, and information shape, then wait for the user's choice. Never silently select a profile or treat Prime as a frozen template.

After the profile is chosen, read only its `profiles/{profile}.json` manifest. Preserve its character through hierarchy, spacing, color meaning, and composition; the manifest guides but does not dictate a fixed layout.

## Use Founder learning safely

After profile selection, use `tools/learning-store.py` and `query_relevant` to query only relevant learning for this artifact's scope. Preserve rule `origin`, `scope`, and `source_generation`. Check explicit Founder feedback for overlap with active learning before persistent activation. A potential or direct conflict blocks mutation; present exactly: KEEP OLD / OVERRIDE / SCOPE SPLIT / ONE-OFF EXCEPTION. Agent inference stays candidate-only. Apply a one-off exception only to its named generation; never carry it forward. Normal GENERATE mode is read-only for profiles, library, and canon. Follow `knowledge/learning-protocol.json` for authority and resolution details.

## Retrieve narrowly

Use `tools/search-catalog.py` with the chosen profile and information roles to shortlist patterns. Inspect metadata first, then open only relevant manifests and references needed for a composition decision. Do not enumerate or preload the library; avoid broad `find library` or `rg --files library` inventories. Master files and encyclopedias must never be preloaded; consult a specific source only when a concrete decision requires it. Search is a shortlist, not an automatic design choice. Briefly explain why the selected pattern or combination fits.

## Compose and build

Choose a composition that follows the information: decision, evidence, comparison, sequence, architecture, or narrative. Combine patterns only when each serves a distinct role. Keep claims, numbers, assumptions, and source boundaries faithful; label illustrative or uncertain material. Use semantic HTML and CSS by default. Add SVG, Canvas, D3, React, or another framework only when it materially improves clarity or interaction.

For a self-contained report, build a standalone artifact. Keep copy readable, accessible, and appropriate to the profile. Do not add data, claims, or decorative motion.

## Review before delivery

Render and inspect desktop and mobile views with `tools/render-preview.mjs`. Check legibility, hierarchy, clipping, direction, contrast, and overflow at both sizes. Maximum 2 automatic repair rounds; render and inspect after the second. If material defects remain, report them instead of calling the output complete.

Deliver the artifact path and a concise account of the chosen profile, composition, responsive review, and any unresolved issue. Do not claim visual verification without inspecting both rendered sizes. For PoV work, stop at the Founder verdict; do not begin a later plan without explicit approval.
