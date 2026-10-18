---
id: 03
name: Deterministic Completion Gate
grade: "C"
graded: 2026-10-18
topic: "Hooks"
evidence_models:
  - "GPT-5 (negative force only)"
  - "Claude Code 2.1.246 (model not stated)"
catalog: v0
---

# Deterministic Completion Gate

**Grade:** C · **Graded:** 18 Oct 2026 · **Topic:** Hooks

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Instructions to run checks are advisory. Anthropic's own docs call CLAUDE.md "context, not enforced configuration" ([memory docs](https://code.claude.com/docs/en/memory)). In Claude Code #40117, the reporter says Opus 4.6 used `--no-verify`, `git stash` and quiet flags despite project rules, landing six consecutive commits with failing tests and up to 63 failures in one commit ([#40117, anecdote](https://github.com/anthropics/claude-code/issues/40117)). Its "closed not planned" status comes only from a secondary source ([pydevtools](https://pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/)). OpenAI reported a training agent adding a pytest hook that skipped every test (vendor report) ([OpenAI](https://openai.com/index/chain-of-thought-monitoring/)).

## Context

The pattern is for unattended or background runs where nobody watches the stop. The check must finish inside hook timeouts: Codex's default is 600 s ([Codex hooks](https://learn.chatgpt.com/docs/hooks)), and Copilot's is 30 s, configurable with `timeoutSec` ([Copilot hooks](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks)). It fits flaky suites and exploratory work poorly. As a counterpoint, OpenAI's harness team runs minimal blocking merge gates and reruns flaky tests (vendor claim) ([OpenAI](https://openai.com/index/harness-engineering/)).

## Trade-offs

Gates can loop. Claude Code overrides a Stop hook after 8 consecutive blocks with no tool call in between ([hooks guide](https://code.claude.com/docs/en/hooks-guide)), Cursor caps stop follow-ups at `loop_limit` 5 ([Cursor hooks](https://cursor.com/docs/agent/hooks)), and forced Copilot turns count against the job timeout ([reference](https://docs.github.com/en/copilot/reference/hooks-reference)). Feedback raises the pressure to game: ImpossibleBench's feedback loop raised cheating from 33% to 38% ([ImpossibleBench](https://arxiv.org/html/2510.20270v1)). Hooks fail open on syntax errors or missing scripts in one practitioner's tests ([yurukusa](https://leanpub.com/claude-md-under-test)), and Cursor hooks fail open unless `failClosed: true` is set. Prefix-matching deny rules and PATH shims can be bypassed, for example by calling `/usr/bin/git` ([pydevtools](https://pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/)).

## Solution

Move the check out of the prompt and into the harness. A hook runs at the stop, commit or tool event, runs the check deterministically, and blocks, feeding the failure text back as the agent's next input. Layer it as in-loop hook, then pre-commit, then CI as the backstop the agent cannot skip ([pydevtools](https://pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/)). Böckeler places computational sensors in the first self-correction loop and again after integration (practitioner claim) ([Böckeler](https://martinfowler.com/articles/harness-engineering.html)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `Stop` / `SubagentStop` returning `{"decision":"block","reason":...}`, or `TaskCompleted`, in `.claude/settings.json`. Exit 2 blocks. Exit early when `stop_hook_active` is true. Handler types are command, http, mcp_tool, prompt and agent (experimental) ([hooks](https://code.claude.com/docs/en/hooks)). |
| Cursor | `.cursor/hooks.json` `stop` returns `followup_message`, which is auto-submitted; `subagentStop` works the same way ([hooks](https://cursor.com/docs/agent/hooks)). |
| Codex | `.codex/hooks.json` or `[[hooks.Stop]]` with `decision: "block"`. Only command and mcp_tool handlers run, and project hooks need a trusted `.codex/`. **Cloud orchestration does not support command hooks**, so rely on AGENTS.md plus CI there ([hooks](https://learn.chatgpt.com/docs/hooks)). |
| GitHub Copilot | `.github/hooks/*.json` on the default branch with `agentStop` returning `decision: "block"` (confirmed in docs, 18 Oct 2026); a `reason` field is **not confirmed**. Copilot CLI also reads `.claude/settings.json` hooks. Built-in validation acts as a vendor-managed gate (vendor claim) ([reference](https://docs.github.com/en/copilot/reference/hooks-reference); [changelog](https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents)). |

## Detection

A stop-type hook (`hooks.Stop|SubagentStop|TaskCompleted`, Cursor `stop`, Codex `[[hooks.Stop]]`, Copilot `agentStop`) whose command matches a test, lint or build command. Plus a commit layer (`.pre-commit-config.yaml`, `.husky/pre-commit`, `lefthook.yml`) and a `pull_request` CI job running the same commands. Branch-protection required checks need the API, not a static check.

## Prediction

False "done" claims, PRs failing CI and commits with failing tests go down. Tokens and wall-clock go up. Test-tampering attempts may *rise* unless [Protected Oracle](02-protected-oracle.md) is in place.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| None | — | — | — | — | **No study compares a deterministic stop gate with no gate** |
| [Spotify](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3) | Practitioner experiment; inferential gate, not deterministic | "Thousands" of sessions; no exact n | n/a | Not stated | LLM judge vetoes ~25% of sessions; agent course-corrects ~50% of the time; judge itself not evaluated |
| [yurukusa](https://leanpub.com/claude-md-under-test) | Practitioner experiment; counterpoint on advisory rules | 39 trials | 22 vs 17 (Japanese), 3 vs 3 (English) | Claude Code 2.1.246 | Banned command attempted 0/22 with rule in CLAUDE.md vs 17/17 without |
| [ImpossibleBench](https://arxiv.org/html/2510.20270v1) | Peer-reviewed; **negative force** | See [Protected Oracle](02-protected-oracle.md) | Up to 10 submissions | GPT-5 and others | Feedback raised cheating 33% → 38% while legitimate pass rose 80% → 83% |

## Related patterns and anti-patterns

[Executable Done-Criteria](01-executable-done-criteria.md) supplies the check and [Protected Oracle](02-protected-oracle.md) is its required companion. The anti-patterns are the *Advisory-Only Gate* and the *Unbounded Gate* (no loop guard, or a gate over a flaky suite).

## Maturity

**Grade: C.** Every major agent ships a blocking stop hook, and vendor docs and practitioners consistently recommend it. No controlled or before/after measurement exists: the only numbers are for an LLM-judge gate and a negative force.
