---
id: 14
name: Paired Multi-Run Evaluation
grade: "A"
graded: 2026-10-18
topic: "Measurement"
evidence_models:
  - "6 model-scaffold pairs (Bjarnason et al.)"
  - "254 SWE-bench submissions (Liu et al.)"
catalog: v0
---

# Paired Multi-Run Evaluation

**Grade:** A · **Graded:** 18 Oct 2026 · **Topic:** Measurement

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Single-run before/after claims hide noise and harness-model interaction. "Temperature 0 does not result in determinism": single-run pass@1 varies by 2.2–6.0 pp ([Bjarnason et al.](https://arxiv.org/html/2602.07150v2)). Headline harness wins often lack run counts. LangChain's +13.7 pp on an 89-task benchmark, where one task is about 1.1 pp, came from bundled changes with no run count, though the authors write "We only changed the harness." ([LangChain](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)). Meta-Harness could not reproduce ForgeCode's 81.8% from its public code ([Meta-Harness](https://arxiv.org/html/2603.28052v1)). Perception misleads: METR's developers forecast a 24% speedup and measured a 19% slowdown (16 developers, 246 tasks) ([METR RCT](https://arxiv.org/abs/2507.09089)).

## Context

The pattern applies to any claim that a harness change helps, and is essential for effects under about 3 pp. Benchmark choice matters: SWE-bench Verified is near saturation ([Mehtiyev & Assunção](https://arxiv.org/pdf/2604.02547)), while TB 2.0 still shows 14–17 pp same-model spreads among visible top entries ([CodeSOTA snapshot](https://www.codesota.com/benchmark/terminal-bench)).

## Trade-offs

Runs cost money: Hack-Verifiable TB spent about $2.5K on 2,225 traces ([Roth et al.](https://arxiv.org/pdf/2608.22103)). Graders can be wrong; Anthropic's CORE-Bench score moved from 42% to 95% after grader and scaffold fixes ([Anthropic evals guide](https://anthropic.com/engineering/demystifying-evals-for-ai-agents)). Results go stale with each model release, because "the space of interesting harness combinations doesn't shrink as models improve" ([Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps)).

## Solution

Run the baseline and the changed harness on the same task set, drawn from real failures (20–50 tasks to start), from a clean environment per trial ([Anthropic evals guide](https://anthropic.com/engineering/demystifying-evals-for-ai-agents)). Use about 9 runs per arm for a 2 pp effect, or about 36 for 1 pp. Report pass@1 with confidence intervals plus pass@k and pass^k ([Bjarnason et al.](https://arxiv.org/html/2602.07150v2)). Record the model-harness pair and version machine-readably, and publish tiers, not ranks ([Liu et al.](https://arxiv.org/pdf/2609.17394)). Run at least 20 pilot runs and then a power analysis ([Jarmak](https://arxiv.org/pdf/2608.13867)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | Headless `claude -p` runs, used by Spence across 22 prompts × 2 in sandboxes ([Spence](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals)); `claude plugin eval` graders ([skills docs](https://code.claude.com/docs/en/skills)). |
| Cursor | No repo-level eval tooling in the research. Cursor's own A/Bs publish no n ([Cursor](https://cursor.com/blog/dynamic-context-discovery)). |
| Codex | No eval tooling documented in the research. Codex CLI was the harness in Jain's 10-runs-per-arm study ([Jain](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html)). |
| GitHub Copilot | No repo-level eval tooling in the research. GitHub ran an online A/B for tool reduction without publishing n ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-were-making-github-copilot-smarter-with-fewer-tools/)). |

## Detection

*A proposed check, not taken from a source.* An `evals/` or similar directory with a task set, a trial count of 3 or more per task, results that record model and harness version, and a CI job that reruns evals when harness files (`AGENTS.md`, `.claude/`, hooks) change.

## Prediction

Reported harness effects shrink toward true values, and false-positive claims fall. Claims under about 3 pp from single runs get labelled indicative.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [Bjarnason et al.](https://arxiv.org/html/2602.07150v2) | arXiv | ~60,000 SWE-bench Verified trajectories, 6 configs | 10 per config | 6 model-scaffold pairs | Single-run spread 2.2–6.0 pp; ~9 runs for 2 pp; pass@1 34.4% vs pass@5 52.9% vs pass^5 15.5% |
| [Liu et al.](https://arxiv.org/pdf/2609.17394) | arXiv, observational | 254 submissions | 1 each | Many | Interaction −15.1 pp (p<0.001); additive model R² = 0.989 |
| [Jarmak](https://arxiv.org/pdf/2608.13867) | arXiv | 1,750 trajectories in one case | Varied | Not stated | Bootstrap with <10 runs had ~10% false positives vs nominal 5%; 100% submitted vs 44% resolved |
| [PatchDiff](https://arxiv.org/pdf/2503.15223) | Peer-reviewed (ICSE '26) | 877 plausible patches | n/a | 3 agents | Resolution rates inflated by 6.4 pp on average |

## Related patterns and anti-patterns

This pattern is the method behind every grade upgrade in this catalog. The anti-pattern is the *Single-Run Victory Lap*.

## Maturity

**Grade: A.** Variance and interaction are measured and replicated, and the method is standard statistics. Adoption is what is rare.
