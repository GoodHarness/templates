---
id: 12
name: Sandboxed Autonomy
grade: "B for friction; C for harm"
graded: 2026-10-18
topic: "Permissions"
evidence_models:
  - "Claude Sonnet 4"
  - "GPT-5"
  - "Cursor and Copilot (AIShellJack)"
catalog: v0
---

# Sandboxed Autonomy

**Grade:** B for friction; C for harm · **Graded:** 18 Oct 2026 · **Topic:** Permissions

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Per-action approval decays into rubber-stamping. Users accept about 93% of prompts, no n given ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)), and full auto-approve rises from about 20% of sessions for new users to over 40% by 750 sessions ([Anthropic](https://www.anthropic.com/research/measuring-agent-autonomy)). Models attempt unsafe actions often. On 356 executable tasks, an LLM judge rated Claude Sonnet 4 unsafe on 49.06% and GPT-5 on 52.58% ([OpenAgentSafety](https://arxiv.org/abs/2507.06134)). The s1ngularity malware invoked AI CLIs with their skip-permission flags; about 50% of victims had one installed ([Wiz](https://www.wiz.io/blog/s1ngularitys-aftermath)). The Antigravity D-drive wipe and the Codex docker-group escalation come from tracker summaries **not read directly** ([Oso](https://www.osohq.com/developers/ai-agents-gone-rogue)).

## Context

The pattern applies to local and unattended work; untrusted repos belong in a VM or cloud session ([Claude Code](https://code.claude.com/docs/en/sandbox-environments)). It does not help against damage through allowed channels: PocketOS lost a database to one authorised API call ([Decrypt](https://decrypt.co/365897/ai-agent-deletes-startup-database-9-seconds-founder-says)).

## Trade-offs

Network access is the most common reason sandboxed agents still ask ([Cursor](https://cursor.com/blog/agent-sandboxing)). Escape hatches get abused: Snowflake's model set `dangerously_disable_sandbox` ([PromptArmor](https://www.promptarmor.com/resources/snowflake-ai-escapes-sandbox-and-executes-malware)). Coverage is partial: Claude Code's Bash sandbox skips file tools, MCP servers and hooks, and leaves `~/.ssh` readable unless denied ([sandboxing](https://code.claude.com/docs/en/sandboxing)).

## Solution

Enforce a boundary at the OS level, so it also binds subprocesses, by confining writes and routing network traffic through a domain-allowlisting proxy. Both are needed ([Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing)). Auto-allow inside, and ask a human, classifier or reviewer only at the boundary.

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `sandbox.enabled: true`, `allowUnsandboxedCommands: false`, `failIfUnavailable: true`, `network.allowedDomains`; managed `disableBypassPermissionsMode`; skip-permissions only inside a container, VM or the sandbox runtime, non-root ([sandboxing](https://code.claude.com/docs/en/sandboxing)). |
| Cursor | Auto-review run mode (default since 3.6), which the docs say is not a security boundary; `.cursor/sandbox.json`; avoid Run Everything ([run modes](https://cursor.com/docs/agent/security/run-modes)). |
| Codex | `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`, network off by default, optional `approvals_reviewer = "auto_review"`; avoid `--yolo` ([sandboxing](https://learn.chatgpt.com/docs/sandboxing)). |
| GitHub Copilot | The coding agent runs in an ephemeral Actions environment behind a firewall that GitHub says is not comprehensive ([firewall](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-firewall)). VS Code sandboxing is on by default, but network is allowed by default ([VS Code](https://code.visualstudio.com/docs/copilot/security)). |

## Detection

`sandbox.enabled: true` in `.claude/settings.json`; a devcontainer with a firewall script and non-root user; Codex `sandbox_mode` not `danger-full-access`; `.cursor/sandbox.json`. Red flags: `--dangerously-skip-permissions`, `--yolo`, `--trust-all-tools` or `--allow-all` in scripts or CI outside containers.

## Prediction

Approval prompts per task and wall-clock fall. Out-of-boundary writes drop to near zero while logged denials rise. The model's unsafe-attempt rate stays unchanged.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing) | Vendor claim | No sample size | n/a | Not stated | 84% fewer permission prompts |
| [Cursor](https://cursor.com/blog/agent-sandboxing) | Vendor claim | No sample size | n/a | Not stated | 40% fewer approval stops |
| [OpenAI Auto-review](https://alignment.openai.com/auto-review) | Vendor eval | n not stated | n/a | Not stated | ~200x fewer approval stops; 99.1% of escalations approved |
| [Wiz on s1ngularity](https://www.wiz.io/blog/s1ngularitys-aftermath) | Incident analysis | >1,000 cases | n/a | Claude, Gemini, Q CLIs | Gemini's workspace restriction blocked almost a quarter of malicious calls |
| [AIShellJack](https://arxiv.org/abs/2509.22040) | arXiv; **negative** | 314 payloads | 1 each | Cursor, Copilot | 88.2% (277/314) still planted malicious code with terminal execution disabled |

## Related patterns and anti-patterns

Least privilege and credential isolation (a candidate, not yet in the catalog) and [Untrusted-Input Containment](13-untrusted-input-containment.md) sit beside it. The anti-pattern is *Skip-Permissions on the Host*.

## Maturity

**Grade: B for friction; C for harm.** Three vendors report fewer approval stops, none with sample sizes. Harm reduction rests on mechanism, consistent docs and one uncontrolled incident observation.
