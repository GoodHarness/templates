---
id: 08
name: Read-Only Sub-agents
grade: "B"
graded: 2026-10-18
topic: "Sub-agents"
evidence_models:
  - "Opus 4"
  - "Sonnet 4"
  - "GPT, Gemini and Claude families (Google study)"
catalog: v0
---

# Read-Only Sub-agents

**Grade:** B · **Graded:** 18 Oct 2026 · **Topic:** Sub-agents

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Exploration output fills the main context, and long inputs degrade accuracy. Across 18 models, focused inputs of about 300 tokens beat full inputs of about 113k tokens on LongMemEval ([Chroma](https://www.trychroma.com/research/context-rot)). Sub-agents fail too when context does not transfer. One spawned agent ignored the parent's CLAUDE.md and falsely reported 35% of records missing when 100% were present ([#15993](https://github.com/anthropics/claude-code/issues/15993)). Another run spawned agents that each re-read the same files ([#27645](https://github.com/anthropics/claude-code/issues/27645)), and Anthropic saw early systems spawn 50 sub-agents for simple queries ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## Context

Use it when output is verbose and only a summary is needed, or the work is parallelizable: centralized multi-agent setups gained +80.9% on Finance-Agent. Avoid it for sequential work, where every multi-agent variant lost 39–70% on PlanCraft ([Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)). Anthropic notes coding has fewer parallelizable subtasks ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## Trade-offs

Token cost multiplies: multi-agent systems used about 15x chat tokens ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)), and five parallel sub-agents use about five times one agent's tokens ([Cursor](https://cursor.com/docs/context/subagents)). A non-fork sub-agent sees only its delegation message ([Claude Code](https://code.claude.com/docs/en/sub-agents)). Errors amplified up to 17.2x for independent agents versus 4.4x centralized ([Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).

## Solution

Delegate noisy, self-contained read work to a fresh context that returns about 1,000–2,000 tokens ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)), scoped to read-only tools, with a single writer. Cognition now endorses read-only sub-agents and clean-context reviewers while keeping its warning against parallel-writer swarms ([Cognition](https://cognition.com/blog/multi-agents-working)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `.claude/agents/<name>.md` with `tools: Read, Grep, Glob`, `model`, optional `isolation: worktree`; built-in Explore and Plan ([docs](https://code.claude.com/docs/en/sub-agents)). |
| Cursor | `.cursor/agents/<name>.md` (also reads `.claude/agents/`) with `readonly: true`; built-in Explore ([docs](https://cursor.com/docs/context/subagents)). |
| Codex | `.codex/agents/<name>.toml`; built-in `explorer`. Delegation happens only when asked or when AGENTS.md or skills instruct it ([docs](https://learn.chatgpt.com/docs/agent-configuration/subagents.md)). |
| GitHub Copilot | `.github/agents/<name>.agent.md` with `tools: ["read","search"]`. The CLI runs custom agents as sub-agents, and VS Code uses `runSubagent`. The cloud agent page does not document sub-agents ([CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli); [VS Code](https://code.visualstudio.com/docs/copilot/agents/subagents)). |

## Detection

Glob the four agent-definition paths. Parse `tools` or `readonly` and flag agents with Edit, Write or Bash as writer sub-agents. Check that each description says when to delegate, look for a cheaper `model` on read-only agents, and check for delegation rules in AGENTS.md (needed for Codex).

## Prediction

Main-context and peak tokens fall on exploration-heavy tasks while total tokens and cost *rise*. Success rises on parallelizable read-heavy work and falls on sequential edits.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [Anthropic multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system) | Vendor eval, research not coding | Internal eval (~20 queries early) | Not stated | Opus 4 lead, Sonnet 4 sub-agents | +90.2% vs single Opus 4; ~15x chat tokens |
| [Google scaling study](https://arxiv.org/html/2512.08296v2) | Controlled study | 180 configs, 5 architectures, 4 benchmarks | Not stated | GPT, Gemini, Claude families | +80.9% parallelizable; **−39% to −70% sequential** |
| [Cognition](https://cognition.com/blog/multi-agents-working) | Vendor anecdote | Method not stated | n/a | Devin | Clean-context reviewer catches 2 bugs per PR, ~58% severe |

## Related patterns and anti-patterns

[Independent, Execution-Grounded Review](10-independent-execution-grounded-review.md) uses a clean-context reviewer, and [Tool Budget](06-tool-budget.md) scopes tools per agent. The anti-patterns are *Parallel-Writer Swarms* and the *Telephone Game*, a vague delegation message without the parent's constraints.

## Maturity

**Grade: B.** Vendor numbers and one controlled multi-agent study show the effect is strongly task-dependent. No source measures read-only sub-agents in a coding harness, which is the specific pattern recommended.
