# Skill-Free Pressure Baseline

Model: `gpt-6-luna` via three fresh ephemeral Codex CLI processes; reasoning effort `low`.
Control: `aion-omega-html` was not installed or loaded. Each valid run explicitly instructed Codex not to invoke/read an installed skill or custom workflow; logs confirm no skill file was read. Responses and logs were retained in `/tmp/aion-clean-baseline-ZpYHr5/` during this run, not in the source repository.

| Scenario | Observed behavior | Required AION behavior absent? | Evidence |
|---|---|---|---|
| Profile gate | Codex generated a board report directly, chose a recommendation and visual direction, and did not recommend a named profile or wait for confirmation. | Yes | Response: “Delay the launch by two weeks” and “A restrained, board-ready layout…” |
| Narrow retrieval | Codex listed the 80 reference paths, read `catalog.ndjson`, then opened only `pattern-02.html`, `pattern-06.html`, `pattern-08.html`, and `pattern-18.html`. It did not read the broad library contents. | No; search-first/narrow selection already appeared in this run. Retain the AION contract because the Architecture Spec independently requires narrow retrieval. | CLI log shows the path listing; response names the catalog and four opened files. Fixture references in `/tmp` were metadata placeholders, so this only measures retrieval breadth, not visual-reference quality. |
| Capability restraint | Codex selected “plain static HTML with embedded CSS” and said React, Astro, and D3 would add unnecessary complexity. | No; the default was already chosen. Retain the AION contract because the Architecture Spec independently defines HTML/CSS as default. | Response text in `03-control-response.txt`. |

Invalid attempt: the first profile-gate invocation auto-read the pre-existing `omega-html-v2` skill and attempted a memory bootstrap; it is excluded from the baseline. The valid control was rerun in a fresh ephemeral process with custom skills explicitly disabled for that run. No old skill or repository files were changed.

# Post-Skill Pressure Results

Model: three fresh `codex exec` processes with `gpt-6-luna`; source repository read-only. The exact source `SKILL.md` was copied byte-for-byte to `~/.agents/skills/aion-omega-html/SKILL.md` for discoverability and each run was instructed to load that file. No other skill file was read. CLI logs and outputs are retained under `/tmp/aion-task10-*.log` during this run.

| Scenario | Observed behavior | Result | Evidence |
|---|---|---|---|
| Profile gate | With no profile supplied, the skill read its contract and recommended Gold for the board audience, then waited for the user's choice before building. | PASS | `/tmp/aion-task10-profile.log`; response offered the four defined profiles and no report. |
| Narrow retrieval | An initial run stopped at the profile gate. With explicit Silver, the first retrieval run searched the catalog and inspected two relevant timeline references, but its initial `rg --files` inventoried the whole library. I tightened the skill to forbid broad `find library` and `rg --files library` inventories. The rerun used the actual 27-entry catalog, called `tools/search-catalog.py` with Silver and incident/timeline/evidence roles, opened only `library/timeline/incident-sequence/reference.html` and `library/timeline/evidence-timeline/reference.html`, and reported that the prompt's generic count of 80 did not match this repository. | PASS after one skill change | `/tmp/aion-task10-retrieval-explicit.log` shows the broad listing that failed; `/tmp/aion-task10-retrieval-fixed.log` shows the narrow rerun and final artifact. |
| Capability restraint | With Prime explicitly selected, the skill generated a standalone responsive report using HTML/CSS. It did not use React, Astro, or D3. The user prohibited file writes, so the response disclosed that desktop/mobile rendering was not run. | PASS for stack choice; visual render not exercised | `/tmp/aion-task10-capability.log`; report was returned inline and source repository remained read-only. |

The retrieval scenario exposed one loophole: path enumeration was happening before narrow selection. The skill now explicitly rules out broad file inventories, and the rerun passed. The static-report case tested implementation choice; rendered desktop/mobile inspection remains covered by the corpus preview runs, not this no-write pressure prompt.
