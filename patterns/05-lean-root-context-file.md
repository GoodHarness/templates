---
id: 05
name: Lean Root Context File
grade: "B (the generated-file downside is A)"
graded: 2026-10-18
topic: "Context files"
evidence_models:
  - "Sonnet-4.5"
  - "GPT-5.2"
  - "GPT-5.1 mini"
  - "Qwen3-30b"
  - "claude-sonnet-4-6"
  - "gpt-5.5"
  - "gpt-5.2-codex"
  - "Claude Sonnet 5"
  - "GPT 6 Luna"
catalog: v0
---

# Lean Root Context File

**Grade:** B (the generated-file downside is A) · **Graded:** 18 Oct 2026 · **Topic:** Context files

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Always-loaded files fill with content the agent could discover itself, plus rules a linter already enforces. In the ETH study, repository overviews appeared in 100% of Sonnet-4.5-generated files and 99% of GPT-5.2-generated ones, did not shorten navigation, and generated files raised cost by 20 to 23% ([Gloaguen et al.](https://arxiv.org/html/2602.11988v3)). In the top 100 repositories, 91 of 100 files have at least one smell and 42% run to 200 lines or more ([dos Santos et al.](https://arxiv.org/html/2606.15828v5)). At MongoDB, the agent reached for `hatch` because AGENTS.md mentioned it, ran a script outside its justfile target and edited generated files. The fix was a terser file with do-not-edit paths ([PYTHON-5889](https://jira.mongodb.org/browse/PYTHON-5889)). Claude Code #2544 collects reports of "MANDATORY" rules being skipped ([issue mirror](https://claudeissues.com/issue/2544-bug-claude-md-mandatory-rules-consistently-ignored-across-multiple-repositories)).

## Context

Every repo with an always-loaded file is in scope. The pattern pays most where knowledge is non-standard or newer than training data. Vercel's Next.js 16 eval rose from 53% to 100% with an AGENTS.md docs index, though the vendor did not publish the eval count, model or run count ([Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)). It pays least for frontier models on well-documented code: frontier rows on Next.js Evals stay at 97% → 97% (pass@4, eval count not stated) ([nextjs.org/evals](https://www.nextjs.org/evals)).

## Trade-offs

Every line is paid for in every session: developer-written files raised cost by up to 19% and added 3.34 steps ([Gloaguen et al.](https://arxiv.org/html/2602.11988v3)). Against that, a missing command means guessing; a curated file cut median wall-clock by 28.64% ([Lulla et al.](https://arxiv.org/html/2601.20404v2)). Vendor caps apply: Codex stops at 32 KiB combined ([docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)), and Claude Code warns at a hardcoded 40,000 characters ([#56406 mirror](https://claudeissues.com/issue/56406-make-the-40-000-char-claude-md-warning-threshold-configurable-or-scale-with-cont)). Drift is the hidden force: agents use a named tool 1.6 times per instance versus fewer than 0.01 times otherwise, so a stale tool name gets followed just as faithfully ([Gloaguen et al.](https://arxiv.org/html/2602.11988v3)).

## Solution

Keep only what the agent cannot infer and would get wrong: exact build, test and lint commands (including a single-test command), required tools, environment quirks, do-not-edit paths, non-default conventions, and pointers to deeper docs. Cut overviews, trees and lint-enforceable rules. Anthropic's per-line test is "Would removing this cause Claude to make mistakes?" ([best practices](https://code.claude.com/docs/en/best-practices)). OpenAI keeps AGENTS.md near 100 lines as "a map, not a 1,000-page instruction manual" ([OpenAI](https://openai.com/index/harness-engineering/)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `./CLAUDE.md` or `.claude/CLAUDE.md`, under 200 lines. `/doctor` proposes cuts, and `/doctor prompt-audit` (v2.1.283+) flags dead references, contradictions and instructions written for older models. AGENTS.md is read natively since v2.1.277, but only when no CLAUDE.md or CLAUDE.local.md exists ([memory docs](https://code.claude.com/docs/en/memory)). |
| Cursor | Root AGENTS.md or `.cursor/rules/*.mdc` with `alwaysApply: true`. Keep rules under 500 lines and add one only after a repeated mistake ([rules docs](https://cursor.com/docs/context/rules)). |
| Codex | Root AGENTS.md, concatenated root to cwd, with a 32 KiB `project_doc_max_bytes` cap ([docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)). |
| GitHub Copilot | `.github/copilot-instructions.md` or AGENTS.md. Code-review guidance is at most about 1,000 lines, starting with 10–20 instructions ([docs](https://docs.github.com/en/copilot/tutorials/customize-code-review)). |

## Detection

A root file exists. Line count is 200 or fewer (Anthropic's target; dos Santos's bloat threshold is 200 or more). Size is 32 KiB or less and under 40,000 characters. The file contains at least one backticked runnable command and no tree glyphs (`├──`, `└──`). An optional LLM pass can flag lint-enforceable rules.

## Prediction

Against a long or generated file, tokens and cost go down while success stays about flat; adherence going up is only a vendor claim. Against no file, frontier-model success stays flat, weaker-model success rises when the file carries non-discoverable knowledge, and time goes down.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [Gloaguen et al. v3](https://arxiv.org/html/2602.11988v3) | arXiv; ICLR 2026 MemAgents workshop oral ([listing](https://iclr.cc/virtual/2026/10021235)) | SWE-bench Lite 300; CTXbench 138 (12 repos) | 1 per agent per task | Claude Code/Sonnet-4.5; Codex/GPT-5.2, GPT-5.1 mini; Qwen Code/Qwen3-30b | LLM files −0.5% (p=0.87) and −2% (p=0.37); dev files +2.4% (p=0.21); dev beat LLM by 7% (p=0.038); cost +20% / +23%. v1 reported +4% / −3%; use v3 |
| [Khatri](https://www.alphaxiv.org/abs/2607.27250) | arXiv, single author; **null** | 17 tasks, 3 repos | 3 repeats (n=45 Claude, n=51 Codex per condition) | claude-sonnet-4-6, gpt-5.5 | None 53.3% vs always-on 55.6% vs selective 55.6%; Codex no effect; MDE >30 pp |
| [Lulla et al.](https://arxiv.org/html/2601.20404v2) | arXiv (ICSE JAWs venue **not verified**) | 124 PRs, 10 repos | Not stated (one implied) | Codex, gpt-5.2-codex | Median wall-clock −28.64%; median output tokens −16.58%; median total tokens +1.29%; correctness not measured |
| [Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) | Vendor eval | Not stated | Retries not stated | Not stated | 53% → 100%; compressing 40KB → 8KB kept 100% |
| [Next.js Evals](https://www.nextjs.org/evals) | Vendor benchmark | Not stated | pass@4 | Frontier and cheaper models | Frontier 97% → 97%; Claude Sonnet 5 81% → 97%; GPT 6 Luna 77% → 87% |
| [Arize](https://arize.com/?p=26585) | Vendor eval (sells the optimisation) | SWE-bench Lite; Django split 114 issues | Not stated | Claude Code, Sonnet 4.5 | Optimised rules +5.19% / +10.87%; baseline and pp-vs-relative not stated |

## Related patterns and anti-patterns

Removed content goes into [Progressive Disclosure via Routed Skills](07-progressive-disclosure-via-routed-skills.md) or into scoped files. Lint rules move to [Teaching Sensors](04-teaching-sensors.md), and drift checks keep the file honest (Context File as Code, a candidate not yet in the catalog). The anti-pattern is the *Generated Encyclopedia*: an `/init` file full of overviews, never pruned.

## Maturity

**Grade: B.** The negative half is A-grade and replicated in direction across ETH, Khatri and Next.js Evals' frontier rows: generated, overview-heavy files add cost without success. No controlled study varies lean versus long as the treatment, and ETH reports no strong length effect, so the positive prescription rests on vendor evals and docs.
