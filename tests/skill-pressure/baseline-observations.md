# Skill-Free Pressure Baseline

Model: `gpt-6-luna` via three fresh ephemeral Codex CLI processes; reasoning effort `low`.
Control: `aion-omega-html` was not installed or loaded. Each valid run explicitly instructed Codex not to invoke/read an installed skill or custom workflow; logs confirm no skill file was read. Responses and logs were retained in `/tmp/aion-clean-baseline-ZpYHr5/` during this run, not in the source repository.

| Scenario | Observed behavior | Required AION behavior absent? | Evidence |
|---|---|---|---|
| Profile gate | Codex generated a board report directly, chose a recommendation and visual direction, and did not recommend a named profile or wait for confirmation. | Yes | Response: “Delay the launch by two weeks” and “A restrained, board-ready layout…” |
| Narrow retrieval | Codex listed the 80 reference paths, read `catalog.ndjson`, then opened only `pattern-02.html`, `pattern-06.html`, `pattern-08.html`, and `pattern-18.html`. It did not read the broad library contents. | No; search-first/narrow selection already appeared in this run. Retain the AION contract because the Architecture Spec independently requires narrow retrieval. | CLI log shows the path listing; response names the catalog and four opened files. Fixture references in `/tmp` were metadata placeholders, so this only measures retrieval breadth, not visual-reference quality. |
| Capability restraint | Codex selected “plain static HTML with embedded CSS” and said React, Astro, and D3 would add unnecessary complexity. | No; the default was already chosen. Retain the AION contract because the Architecture Spec independently defines HTML/CSS as default. | Response text in `03-control-response.txt`. |

Invalid attempt: the first profile-gate invocation auto-read the pre-existing `omega-html-v2` skill and attempted a memory bootstrap; it is excluded from the baseline. The valid control was rerun in a fresh ephemeral process with custom skills explicitly disabled for that run. No old skill or repository files were changed.
