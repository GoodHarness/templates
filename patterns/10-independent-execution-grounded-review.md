---
id: 10
name: Independent, Execution-Grounded Review
grade: "B (self-review unreliability A)"
graded: 2026-10-18
topic: "Workflows, sub-agents"
evidence_models:
  - "GPT-3.5"
  - "GPT-4"
  - "gpt-5-codex"
catalog: v0
---

# Independent, Execution-Grounded Review

**Grade:** B (self-review unreliability A) · **Graded:** 18 Oct 2026 · **Topic:** Workflows, sub-agents

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Agents grade their own work as done. Without external feedback, self-correction made models worse: GPT-3.5 on CommonSenseQA fell from 75.8 to 38.1 after one round, and GPT-4 on GSM8K fell from 95.5 to 91.5 to 89.0 ([Huang et al., ICLR 2024](https://arxiv.org/html/2310.01798v2)). Anthropic says agents praise their own mediocre work (vendor claim) ([Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps)). METR found 0 of 15 reviewed agent PRs mergeable as-is, including test-passing ones ([METR](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons)).

## Context

Value rises with how long the agent ran unattended ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). Review does not replace a human: Claude Code Review never approves or blocks, and Copilot review does not count toward required approvals by default ([Claude Code Review](https://code.claude.com/docs/en/code-review); [Copilot](https://docs.github.com/en/copilot/concepts/agents/code-review)).

## Trade-offs

Claude Code Review costs $15–25 per review and averages about 20 minutes (vendor claim) ([Anthropic](https://claude.com/blog/code-review)). At Beko, PR closure time *rose* from 5h52m to 8h20m (p<0.001), though the paper's conclusion inconsistently cites 50 to 48 minutes ([Cihan et al.](https://arxiv.org/html/2412.18531v2)). A reviewer told to find gaps usually reports some, which invites over-engineering ([best practices](https://code.claude.com/docs/en/best-practices)). The instruction source is an attack surface. Claude Code Review and Bugbot read config from the base branch, while Copilot code review reads instructions from the head branch, the one containing the changes ([Copilot](https://docs.github.com/en/copilot/concepts/agents/code-review); [Bugbot](https://cursor.com/docs/bugbot)).

## Solution

Give the reviewer only the diff, the criteria and tools (repo access, execution, browser), not the writer's reasoning. Ground it in external signal, the one condition under which self-correction research finds correction works ([Kamoi et al.](https://arxiv.org/abs/2406.01297); [Olausson et al.](https://arxiv.org/abs/2306.09896)). Add a verification stage to filter false positives.

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | The `/code-review` skill runs in a fresh subagent. The Code Review GitHub app uses parallel agents, a verification step and `REVIEW.md`. Custom reviewers go in `.claude/agents/` ([docs](https://code.claude.com/docs/en/code-review)). |
| Cursor | Agent Review in the editor; Bugbot on PRs (`.cursor/BUGBOT.md`, base-branch YAML); a read-only Verifier subagent example ([Bugbot](https://cursor.com/docs/bugbot); [subagents](https://cursor.com/docs/subagents)). |
| Codex | `/review` or `codex review --uncommitted|--base|--commit`, with `code_review.md` referenced from AGENTS.md ([best practices](https://learn.chatgpt.com/guides/best-practices)). The `review_model` setting and the custom-subagent format are **not verified**. |
| GitHub Copilot | Copilot code review reads instruction files and AGENTS.md. The coding agent runs CodeQL, secret scanning and Copilot review on its own changes (vendor claim) ([changelog](https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-automatically-validates-code-security-and-quality/)). |

## Detection

Reviewer agent files (`*review*`, `*verif*`, `readonly: true`); `REVIEW.md`, `.cursor/BUGBOT.md`, `bugbot.yaml`, or `code_review.md`; CI calling `claude -p` or `codex review`; AGENTS.md requiring a fresh-context review. Org rulesets need the API.

## Prediction

Defects reaching human review go down and token cost goes up. PR closure time may rise. Track the comment-addressed rate as the health metric.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [Huang et al.](https://arxiv.org/html/2310.01798v2) | Peer-reviewed; **negative for self-review** | GSM8K 1,319; CommonSenseQA 1,221; HotpotQA 100 | 2 rounds | GPT-3.5, GPT-4 | Accuracy fell without external feedback |
| [OpenAI reviewer](https://alignment.openai.com/scaling-code-verification/) | Vendor eval | >100,000 external PRs per day | n/a | gpt-5-codex reviewer | Code changed after 52.7% of comments; 46% on Codex PRs vs 53% on human PRs |
| [Anthropic Code Review](https://claude.com/blog/code-review) | Vendor claim, no sample size | Internal | n/a | Not stated | Substantive-comment PRs 16% → 54%; <1% of findings marked incorrect |
| [Beko](https://arxiv.org/html/2412.18531v2) | Industry case study | 4,335 PRs, 1,568 reviewed by bot | Observational | GPT-4 (Qodo PR-Agent) | 73.8% of 1,408 comments resolved; closure time rose |
| [Sun et al.](https://arxiv.org/html/2508.18771v1) | arXiv, observational | 178 repos, 3,002 PRs, 22,326 AI comments | n/a | 16 GitHub Actions | Valid AI comments addressed 0.9–19.2% vs ~60% for human comments |

## Related patterns and anti-patterns

[Read-Only Sub-agents](08-read-only-sub-agents.md) supplies clean context, and [Small Units with Checkpoints](11-small-units-with-checkpoints.md) makes diffs reviewable. Findings feed failure-driven harness improvement. The anti-patterns are *Self-Grading*, *Review Theatre* and *Bot as Approver*.

## Maturity

**Grade: B.** The claim that self-review without external feedback is unreliable is replicated (Huang, Olausson, Kamoi), an A-grade leg. Deployed reviewer agents have only vendor numbers and mixed observational studies, and "fresh context beats same context" is untested.
