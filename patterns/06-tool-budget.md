---
id: 06
name: Tool Budget
grade: "A for mechanism; B for coding-task success"
graded: 2026-10-18
topic: "MCP"
evidence_models:
  - "qwen-max-0125"
  - "gpt-4o"
  - "GPT-5"
  - "Sonnet 4.5"
  - "Opus 4"
  - "Opus 4.5"
  - "Sonnet 4.6"
catalog: v0
---

# Tool Budget

**Grade:** A for mechanism; B for coding-task success · **Graded:** 18 Oct 2026 · **Topic:** MCP

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Tool definitions flood context, and selection degrades as tools pile up. One Claude Code user saw about 144,802 tokens of MCP definitions, including 135 tools and about 125,964 tokens from one server, before default tool search existed ([#12241](https://github.com/anthropics/claude-code/issues/12241)). Anthropic reports 58 tools taking about 55K tokens (vendor eval) ([Anthropic](https://anthropic.com/engineering/advanced-tool-use)). GitHub says an oversized toolset made Copilot ignore instructions and call unnecessary tools (vendor claim) ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-were-making-github-copilot-smarter-with-fewer-tools/)). Invariant Labs showed hidden instructions in a tool description making Cursor exfiltrate `~/.cursor/mcp.json` and SSH keys ([Invariant](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)).

## Context

The pattern applies with multiple MCP servers, more than about 10 tools, or definitions over about 10K tokens (Anthropic's threshold for tool search). It matters less with fewer than 10 tools that are all used every session ([Anthropic](https://anthropic.com/engineering/advanced-tool-use)). The code-execution variant needs a sandbox ([Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp)).

## Trade-offs

Deferral adds a search step and can miss tools; fixed five-tool shortlists failed on hard queries ([BoR](https://arxiv.org/abs/2605.24660)). Over-pruning drops capability: Copilot's static list covered 69.0% of needed tools against 94.5% for embedding routing ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-were-making-github-copilot-smarter-with-fewer-tools/)). Claude Code disables tool search behind non-first-party `ANTHROPIC_BASE_URL` proxies and on Azure Foundry ([MCP docs](https://code.claude.com/docs/en/mcp)). The Copilot cloud agent calls tools without approval, so GitHub recommends read-only allowlists ([docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp)).

## Solution

Keep the always-loaded set small and non-overlapping, allowlist the tools you need from each server, and defer the rest behind search. Consolidate and namespace tools; Anthropic's guidance is that "More tools don't always lead to better outcomes" ([Anthropic, writing tools](https://www.anthropic.com/engineering/writing-tools-for-agents)). The code-execution variant exposes tools as files the model codes against, so intermediate data never passes through context.

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `.mcp.json`; tool search on by default (`ENABLE_TOOL_SEARCH`); per-tool `anthropic/alwaysLoad`; `MAX_MCP_OUTPUT_TOKENS` default 25,000; per-subagent `mcpServers` ([MCP docs](https://code.claude.com/docs/en/mcp)). |
| Cursor | `.cursor/mcp.json` with server toggles and enterprise allowlists. Tools have been synced to folders with names-only loading since Jan 2026 ([blog](https://cursor.com/blog/dynamic-context-discovery)). A 40–50 tool warning is from the forum, **unverified by staff**. |
| Codex | `[mcp_servers.<name>]` with `enabled_tools` / `disabled_tools` and per-tool `output_token_limit`. No deferred loading is documented, which is absence of evidence ([MCP docs](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)). |
| GitHub Copilot | A `tools` allowlist is required per server in the cloud agent. VS Code has a 128-tool hard limit per request, a virtual-tools threshold and tool sets ([cloud agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp); [VS Code](https://code.visualstudio.com/docs/copilot/chat/chat-tools)). The Copilot CLI MCP config path is **unconfirmed**. |

## Detection

Count servers in `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json` and `.codex/config.toml`. Check for allowlists (Codex `enabled_tools`, Copilot `tools` not equal to `"*"`), and flag `ENABLE_TOOL_SEARCH=false`. Statically, servers multiplied by known tool counts approximates load; flag more than about 10 always-loaded tools or more than about 10K definition tokens.

## Prediction

Tokens per turn and tool-selection errors go down. Coding success rises modestly, by the +2 to 5 pp Copilot reports. Code execution cuts tokens most on data-heavy, multi-call workflows.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [RAG-MCP](https://arxiv.org/html/2505.03275v1) | arXiv | MCPBench web-search subset, 20 tasks per N | 20 trials per baseline | qwen-max-0125 | Selection 43.13% (retrieval) vs 18.20% (keyword) vs 13.62% (all tools); prompt tokens 1,084 vs 2,133.84 (abstract's "over 50%" vs ~49% in table) |
| [LangChain](https://www.langchain.com/blog/react-agent-benchmarking) | Vendor/practitioner experiment | 2 domains × 30 tasks; up to 14 distractor domains | 3 per task (90 per config) | 5 models | gpt-4o fell to 2% on Calendar at 7 domains; longer trajectories degraded faster |
| [GitHub Copilot](https://github.blog/ai-and-ml/github-copilot/how-were-making-github-copilot-smarter-with-fewer-tools/) | Vendor eval and online A/B | SWE-Lancer, SWE-bench Verified; n not stated | Not stated | GPT-5, Sonnet 4.5 | 40 → 13 tools: +2–5 pp; ~400 ms lower latency |
| [Anthropic Tool Search](https://anthropic.com/engineering/advanced-tool-use) | Vendor eval | n not stated | Not stated | Opus 4, Opus 4.5 | 49% → 74%; 79.5% → 88.1%; −85% tokens (page's figures do not reconcile) |
| [Cursor](https://cursor.com/blog/dynamic-context-discovery) | Vendor A/B | n not stated | Not stated | Not stated | −46.9% total agent tokens in runs calling an MCP tool |
| [BoR](https://arxiv.org/abs/2605.24660) | arXiv (BFCL rated "Flawed" by [Epoch AI](https://epoch.ai/benchmarks/berkeley-function-calling-leaderboard/review)) | BFCL 370 tools; ToolBench 3,251 | Not stated | Sonnet 4.6 | Adaptive shortlists 93.1% vs fixed-5 87.1% |
| [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | Vendor example | One workflow | None | Not stated | 150,000 → 2,000 tokens (98.7%) |

## Related patterns and anti-patterns

Deferred loading is progressive disclosure for tools ([Progressive Disclosure via Routed Skills](07-progressive-disclosure-via-routed-skills.md)). Per-sub-agent tool scoping links to [Read-Only Sub-agents](08-read-only-sub-agents.md), and allowlists link to [Untrusted-Input Containment](13-untrusted-input-containment.md). The anti-pattern is *MCP Sprawl*.

## Maturity

**Grade: A for the mechanism; B for coding-task success.** An arXiv study, a three-run practitioner experiment and several vendor evals replicate the direction: more tools degrade selection, and pruning or deferral helps. The only coding-benchmark effect (+2 to 5 pp) is a vendor figure without n, and the code-execution variant rests on one illustrative example.
