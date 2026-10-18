---
id: 09
name: Plan Gate
grade: "B (agent-side planning for weaker models A; human approval C)"
graded: 2026-10-18
topic: "Workflows"
evidence_models:
  - "Nemotron-3 30B"
  - "Nemotron-3 120B"
  - "Nemotron-3 550B"
  - "Mistral-Medium-3.5-128B"
  - "GPT-5 mini"
  - "DeepSeek-V3"
  - "DeepSeek-R1"
  - "Devstral-small"
catalog: v0
---

# Plan Gate

**Grade:** B (agent-side planning for weaker models A; human approval C) · **Graded:** 18 Oct 2026 · **Topic:** Workflows

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Agents charge ahead on the wrong problem or try to build everything at once; Anthropic reports that "the agent tended to try to do too much at once" ([Anthropic, Nov 2025](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). OCaml maintainers rejected a 13,000+ line Claude Code PR that arrived with no prior design discussion ([DevClass](https://devclass.com/2025/11/27/ocaml-maintainers-reject-massive-ai-generated-pull-request/)). Plan gates also fail. In Claude Code #12154, Claude ran `git checkout` in plan mode and destroyed uncommitted work ([issue mirror](https://claudeissues.com/issue/12154-bug-plan-mode-not-enforced-claude-executes-destructive-commands-despite-plan-onl)). And "a subpar plan hurts performance even more than no plan at all" ([Liu et al.](https://arxiv.org/abs/2604.12147)).

## Context

Use it when the approach is uncertain, the change touches many files, or the code is unfamiliar. Skip it when the diff fits in one sentence. All four vendors give this guidance ([Claude Code](https://code.claude.com/docs/en/best-practices); [Cursor](https://cursor.com/docs/agent/plan-mode); [Codex](https://learn.chatgpt.com/guides/best-practices); [Copilot](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)).

## Trade-offs

Planning cut mean cost per task for the stronger models but raised it for the smallest ([Fan et al.](https://arxiv.org/html/2609.20804)). A plan's influence decays within a session; re-injecting it every 5 steps improved success ([Liu et al.](https://arxiv.org/html/2604.12147)). Approvals become rubber stamps. Heavy specs cost human time: in one practitioner run, spec-kit needed about 57 minutes of agent time plus about 5.5 hours of review against about 32 minutes for plain prompting. The author concluded: "I don't consider it a viable process, at least not in its purest form" ([Eberhardt](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html)).

## Solution

Read-only exploration produces a written plan. A human or the agent checks it against intent before any edit, and implementation runs against that explicit target, with the plan doubling as verification criteria. On a miss, revert and re-plan rather than patching ([Cursor](https://cursor.com/docs/agent/plan-mode)). One variant persists the plan as a durable spec or progress file, such as OpenAI's ExecPlans ([OpenAI cookbook](https://developers.openai.com/cookbook/articles/codex_exec_plans)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | Plan mode via Shift+Tab, `/plan`, `--permission-mode plan` or `"defaultMode": "plan"`; `plansDirectory`; built-in Plan subagent. In interactive sessions with bypass permissions available, plan-mode blocks are **not enforced** ([permission modes](https://code.claude.com/docs/en/permission-modes)). |
| Cursor | Plan Mode writes an editable Markdown plan; "Save to workspace" moves it into the repo ([docs](https://cursor.com/docs/agent/plan-mode)). |
| Codex | `/plan` or Shift+Tab. AGENTS.md can point Codex at a `PLANS.md` ExecPlan template ([best practices](https://learn.chatgpt.com/guides/best-practices)). |
| GitHub Copilot | The VS Code Plan agent writes `/memories/session/plan.md`, which is cleared at session end ([docs](https://code.visualstudio.com/docs/copilot/agents/planning)). The CLI has a plan mode. The cloud agent researches on a branch, with no plan artifact described. |

## Detection

`"defaultMode": "plan"` or `plansDirectory` in `.claude/settings.json`; plan or spec files (`PLANS.md`, `docs/plans/`, `SPEC.md`, `.specify/`); AGENTS.md text requiring a plan. The paths `.kiro/specs/<name>/`, `specs/NNN-feature/` and `aidlc-docs/` are commonly reported but **not verified** in docs. A plan file proves plans are written, not that a human reviewed them.

## Prediction

Success rises on ambiguous, multi-file tasks and with weaker models. Cost per task falls for strong models, and rework falls. Wall-clock rises on small tasks. Success *falls* with poor plans.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect (success with vs without planning) |
|---|---|---|---|---|---|
| [Fan et al.](https://arxiv.org/html/2609.20804) | arXiv ablation | SWE-bench Verified 500; TB 2.1 89 | Not stated; temp 0 | Nemotron-3 30B/120B/550B, Mistral-Medium-3.5-128B | 30B: 25.20% vs 13.60% (SWE), 13.48% vs 8.99% (TB). Larger models flat or slightly lower (e.g., 550B 65.80% vs 67.80%). Only the 30B SWE-bench difference is significant |
| [Liu et al.](https://arxiv.org/html/2604.12147) | arXiv | SWE-bench Verified 497 plus SWE-bench Pro Python; 21,120 trajectories | Not stated | GPT-5 mini, DeepSeek-V3, DeepSeek-R1, Devstral-small | Standard plan beats no plan; subpar plan worse than none; rates only in figures |
| [Eberhardt](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html) | Practitioner experiment; **negative for heavy specs** | 1 developer, 1 feature plus 1 increment | 1 each | Not stated | Plain prompting about 10x faster (author's estimate) |
| [Spec Kit Agents](https://arxiv.org/abs/2604.05278) | arXiv; hooks inside SDD, not SDD vs none | 32 features, 5 repos | 128 runs | Not named | +0.15 on a 1–5 LLM-judge composite (p<0.05) |

## Related patterns and anti-patterns

The plan's task list defines [Small Units with Checkpoints](11-small-units-with-checkpoints.md)'s units, and [Independent, Execution-Grounded Review](10-independent-execution-grounded-review.md) reviews the diff against the plan. The anti-patterns are *Charge Ahead*, *Spec Ceremony* (full SDD for a one-line change) and *Rubber-Stamp Approval*.

## Maturity

**Grade: B overall.** Two independent controlled ablations show agent-side planning helps weaker models on SWE-style benchmarks (an A-grade leg). The human plan-approval gate that practitioners mean has no measurement at all (C).
