---
id: 13
name: Untrusted-Input Containment
grade: "C (problem A)"
graded: 2026-10-18
topic: "Permissions, MCP"
evidence_models:
  - "Claude 4 Sonnet"
  - "Gemini 2.5 Pro"
  - "Claude 4 Opus (incident)"
catalog: v0
---

# Untrusted-Input Containment

**Grade:** C (problem A) · **Graded:** 18 Oct 2026 · **Topic:** Permissions, MCP

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Injected instructions in issues, PRs, READMEs and MCP results hijack agents. A malicious public issue made Claude 4 Opus leak private-repo contents through the GitHub MCP server ([Invariant](https://invariantlabs.ai/blog/mcp-github-vulnerability)). CurXecute (CVE-2025-54135) rewrote `mcp.json` to run commands ([THN](https://thehackernews.com/2025/08/cursor-ai-code-editor-fixed-flaw.html)). Comment and Control hit Claude Code Security Review, Gemini CLI Action and Copilot Agent through PR titles and comments ([SecurityWeek](https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/)). GitLost leaked a private README through a public issue ([Noma](https://noma.security/blog/gitlost-how-we-tricked-githubs-ai-agent-into-leaking-private-repos/)).

## Context

Risk peaks for agents triggered by external events in CI, agents with MCP servers reading external content, and agents with web access plus secrets. Meta's rule: a task needing all three legs should not run autonomously ([Meta](https://ai.meta.com/blog/practical-ai-agent-security/)).

## Trade-offs

CaMeL's design-level defense cost 7 points of utility (84% to 77% on AgentDojo) ([CaMeL](https://arxiv.org/abs/2503.18813)). Allowlisted domains can still exfiltrate; Claude Code's proxy does not inspect TLS by default ([sandboxing](https://code.claude.com/docs/en/sandboxing)), and Copilot's firewall misses MCP servers and setup steps ([firewall](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-firewall)). Classifiers are probabilistic; Willison calls a 95% catch rate "very much a failing grade" ([Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)).

## Solution

Deterministically remove one leg of the trifecta. Cut exfiltration with default-deny egress and method limits. Cut private data with scoped tokens and one repo per session. Cut untrusted input by accepting only trusted authors; Copilot ignores comments from users without write access ([GitHub](https://docs.github.com/en/copilot/concepts/agents/coding-agent/risks-and-mitigations)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `sandbox.network.allowedDomains` (starts empty). `strictAllowlist` only takes effect in user, managed or CLI settings, not repo settings. `mcp__*` deny globs; run MCP servers in a container ([sandboxing](https://code.claude.com/docs/en/sandboxing)). |
| Cursor | Sandbox network blocked except the allowlist plus defaults. No documented control over MCP content trust ([run modes](https://cursor.com/docs/agent/security/run-modes)). |
| Codex | Cloud internet off by default; when on, a domain allowlist plus GET/HEAD/OPTIONS only ([internet access](https://learn.chatgpt.com/docs/cloud/internet-access)). |
| GitHub Copilot | Custom firewall allowlist, write-access-only triggers and hidden-character filtering ([risks](https://docs.github.com/en/copilot/concepts/agents/coding-agent/risks-and-mitigations)). |

## Detection

A narrow `allowedDomains`; `.mcp.json` does not pair content-reading servers with write or post tools; agent workflows do not trigger on `pull_request_target`, `issue_comment` or `issues` from untrusted authors with secrets in env; workflow `permissions:` are read-only. Codex cloud internet, the Copilot firewall and Claude Code cloud network level need an org-settings audit.

## Prediction

Exfiltration success on a fixed injection suite falls with default-deny egress. Code-poisoning success does not. Legitimate success dips slightly.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [AIShellJack](https://arxiv.org/abs/2509.22040) | arXiv | 314 payloads, 5 codebases; 2,826 results | 1 each | Cursor, Copilot with Claude 4 Sonnet and Gemini 2.5 Pro | 41.1% to 83.4% attack success (one Gemini figure internally inconsistent: 73.9% vs 76.8%/77%) |
| [The Attacker Moves Second](https://arxiv.org/abs/2510.09023) | arXiv | 12 published defenses | Adaptive attacks | Various | >90% success against most |
| [CaMeL](https://arxiv.org/abs/2503.18813) | arXiv, outside coding | AgentDojo | Not stated | Not stated | 77% of tasks with provable security vs 84% undefended |
| [Anthropic auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) | Vendor eval | n=1,000 synthetic exfiltration | n/a | Classifier | 5.7% false negatives |

## Related patterns and anti-patterns

[Sandboxed Autonomy](12-sandboxed-autonomy.md)'s proxy is the egress control, and credential isolation cuts the data leg. The anti-pattern is an *Agent in CI on Public Triggers with Secrets*.

## Maturity

**Grade: C (problem A).** Controlled measurements show coding agents are highly injectable and that guardrails fall to adaptive attacks. No study measures egress allowlists, trusted-author triggers or scoped tokens in coding agents.
