---
id: 11
name: Small Units with Checkpoints
grade: "B"
graded: 2026-10-18
topic: "Workflows"
evidence_models:
  - "7 models (Kim et al.)"
  - "5 agents (Ehsani et al.)"
catalog: v0
---

# Small Units with Checkpoints

**Grade:** B · **Graded:** 18 Oct 2026 · **Topic:** Workflows

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Giant diffs go unreviewed and good states get overwritten. In 654 coded rejections, every PR rejected for size was agentic (1.5% of agentic rejections vs 0.0% of human), though 69.0% of rejected agent PRs gave no explicit reason ([Nakashima et al.](https://arxiv.org/html/2602.04226v1)). In five cases the agent produced a patch bit-identical to the gold patch and later destroyed it ([Kim et al.](https://www.alphaxiv.org/abs/2603.24631)). Claude Code checkpoints do not capture Bash changes, and #12154 lost uncommitted work ([best practices](https://code.claude.com/docs/en/best-practices)).

## Context

The pattern applies to any output headed for review or merge, especially from unattended or cloud agents. In-agent decomposition matters less as models improve: Anthropic dropped its sprint construct with Opus 4.6 ([Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps)).

## Trade-offs

More units mean more human context switches. Parallel agents collide on a shared checkout without worktrees ([Cursor](https://cursor.com/docs/subagents)). Copilot iterates on each comment as soon as it lands unless reviewers batch them ([GitHub](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)), and its sessions are capped at 59 minutes ([GitHub](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)).

## Solution

Bound each unit to the agent's reliable horizon and to human review capacity. Persist state between units through commits, a progress file and a pass/fail feature list. Checkpoint each edit that passes tests, and put deterministic gates at unit boundaries.

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | Checkpoints via Esc+Esc or `/rewind` (file-edit tools only), `/clear`, `/batch` across 5–30 worktree subagents, and the long-running pattern: `init.sh`, `claude-progress.txt`, JSON feature list, a commit per feature ([best practices](https://code.claude.com/docs/en/best-practices); [Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). |
| Cursor | Plan to-dos, revert and re-plan, worktree subagents ([docs](https://cursor.com/docs/subagents)). |
| Codex | Goal, context, constraints and done-when prompts; worktrees; `/fork`; ExecPlan Progress checklist ([best practices](https://learn.chatgpt.com/guides/best-practices)). |
| GitHub Copilot | One PR per task on `copilot/` branches. The agent cannot approve or merge its own PR, the requester cannot approve it, and workflows need approval ([risks](https://docs.github.com/en/copilot/concepts/agents/coding-agent/risks-and-mitigations)). |

## Detection

Median and 90th-percentile lines changed per agent PR, using `copilot/` branches or `Co-Authored-By` trailers; a documented maximum PR size; progress artifacts; Stop hooks. Branch protection needs the API.

## Prediction

Merge rate rises; diff size, time to first review and reverts fall. Total human touches rise.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [Ehsani et al.](https://arxiv.org/html/2601.15195v1) | MSR '26, observational | 33,596 agent PRs | n/a | 5 agents | Unmerged PRs ~17% more lines; each failed CI check ~15% lower merge odds |
| [METR time horizons](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) | Replicated measurement of task length, not an intervention | Multiple suites | Multiple | Multiple models | "Almost 100%" success under 4 human-minutes; under 10% beyond ~4 hours (later superseded by TH 1.1) |
| [Kim et al.](https://www.alphaxiv.org/abs/2603.24631) | arXiv | 16,758 trajectories; 5 gold-identical destroyed patches | n/a | 7 models | An edit-commit checkpoint recovered 5 of 5 |
| [Anthropic Code Review](https://claude.com/blog/code-review) | Vendor claim | No sample size | n/a | Not stated | 0.5 issues per PR under 50 lines vs 7.5 over 1,000 lines |

## Related patterns and anti-patterns

[Plan Gate](09-plan-gate.md) defines the units and [Independent, Execution-Grounded Review](10-independent-execution-grounded-review.md) reviews them. The anti-patterns are the *Mega-PR*, the *Kitchen-Sink Session* and *Self-Approval Loops*.

## Maturity

**Grade: B.** Large observational datasets and METR's task-length measurements support it, but no study splits identical work into small versus large units, and the checkpoint component rests on five cases.
