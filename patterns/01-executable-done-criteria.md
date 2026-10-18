---
id: 01
name: Executable Done-Criteria
grade: "A (conditional on externally written checks)"
graded: 2026-10-18
topic: "Workflows, context files"
evidence_models:
  - "GPT-4 Turbo"
  - "Llama 3 70B"
  - "GPT-4o"
  - "GPT-4.1"
  - "GPT-6 Sol"
  - "GPT-6 Luna"
  - "gpt-5.2"
  - "gemini-3-pro"
  - "kimi-k2-thinking"
  - "deepseek-v3.2"
  - "Qwen3-Coder 30B"
catalog: v0
---

# Executable Done-Criteria

**Grade:** A (conditional on externally written checks) · **Graded:** 18 Oct 2026 · **Topic:** Workflows, context files

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Agents stop when the work looks done and report success they never checked. In 26% of failed Terminal-Bench runs the agent ended by claiming success ([Zhao et al.](https://www.alphaxiv.org/abs/2607.09510)), and one Claude Code user reports Opus 4.6 announcing "4966/4966 ALL PASSED" while the golden suite had fallen from 4992/4992 to 4985/4992 ([#46940, anecdote](https://github.com/anthropics/claude-code/issues/46940)). Another reports 60 passed, 0 failed after Claude loosened an assertion and routed around the UI through an API helper ([#33781, anecdote](https://github.com/anthropics/claude-code/issues/33781)). Spotify names PRs that pass CI but are functionally wrong as its most serious failure class (practitioner claim) ([Spotify](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3)). On dotnet/runtime #115762, the Copilot coding agent could not build or test at all because of firewall and configuration blocks ([PR](https://github.com/dotnet/runtime/pull/115762)).

## Context

The pattern applies when a fast, trustworthy, runnable check exists: tests, a typecheck, a build, a fixture diff, or a screenshot compared against a design ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). It is weak when the suite is thin. 29.6% (260/877) of "plausible" SWE-bench Verified patches behave differently from the developer patch ([Wang, Pradel & Liu, ICSE 2026](https://arxiv.org/html/2503.15223v2)). It is also weak when the agent writes its only oracle (see the null result under Evidence). Slow suites need sampling: Carlini's compiler harness added a `--fast` mode that ran a random 1% or 10% of tests ([Anthropic](https://www.anthropic.com/engineering/building-c-compiler)).

## Trade-offs

Tokens and latency rise. Prompting gpt-5.2 to write tests raised output tokens per task by 19.8% with no change in tasks resolved ([Chen et al.](https://arxiv.org/html/2602.07900v1)), and Agentless reproduction tests cost $0.25 per issue ([Xia et al.](https://arxiv.org/html/2407.01489v2)). Returns diminish: remediation gains flattened after 3 to 4 iterations ([Mathews & Nagappan](https://arxiv.org/html/2402.13521v2)). Weak tests breed false confidence: passing patches overstated resolve rates by about 6.4 points ([Wang et al.](https://arxiv.org/html/2503.15223v2)), and maintainer merges ran 24.2 pp below grader scores (SE 2.7) ([METR](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)). A check the agent iterates against also becomes a target, which is why [Protected Oracle](02-protected-oracle.md) exists.

## Solution

Name the exact check (test, lint, typecheck and build commands, a screenshot for UI) in the context file or the task. Require the agent to show evidence, meaning the command and its output, before claiming done. Prefer checks authored outside the implementing context. The mechanism is a binary environmental signal in place of self-judgment: Self-Debugging matched baselines that sampled more than 10x as many candidates by reusing execution feedback ([Chen et al., ICLR 2024](https://arxiv.org/abs/2304.05128)). The TDAD authors put the lesson as "context (which tests to check) outperforms procedure (how to do TDD)" ([Alonso et al.](https://arxiv.org/html/2603.17973v2)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | Test and lint commands in CLAUDE.md. Criteria in the prompt. `/goal` makes a separate evaluator re-check every turn. A verification subagent or the bundled `/code-review` skill gives a second check ([best practices](https://code.claude.com/docs/en/best-practices)). |
| Cursor | Commands in AGENTS.md or an Always Apply `.cursor/rules/*.mdc`. The built-in lint-reading tool fixes errors in just-edited files for about 3 iterations. Staff say this is model behaviour, not guaranteed, and it is IDE-only, absent in the CLI and Cloud Agents ([forum](https://forum.cursor.com/t/does-agents-iterate-on-lint-errors-work-with-custom-third-party-lsp-servers-or-only-built-in-linters/168705)). No built-in "run tests before finishing" step is documented. |
| Codex | Commands in AGENTS.md (32 KiB default cap) ([docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)). The launch-era claim that the codex-1 system message runs AGENTS.md checks comes from a page now marked outdated, and current docs are silent: **not verified as current** ([OpenAI, May 2025](https://openai.com/index/introducing-codex/)). |
| GitHub Copilot | Instruction files plus `copilot-setup-steps.yml` to preinstall tooling ([docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)). Built-in validation (tests, linter, CodeQL, Advisory DB, secret scanning, Copilot code review) is on by default, per a vendor claim ([changelog](https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/)). |

## Detection

A context file (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`) contains at least one runnable verify command matching a pattern such as `pytest|go test|cargo (test|clippy)|(npm|pnpm|yarn) (run )?(test|lint|typecheck|build)|tsc|ruff|mypy|eslint`. The named command resolves in `package.json`, `Makefile` or `pyproject.toml`. Test files exist. For Copilot, `copilot-setup-steps.yml` is present ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)).

## Prediction

Task success goes up, false "done" claims go down, and tokens and latency per task go up. The effect should scale with test quality and should be about zero when the agent writes the only tests.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [TGen, ASE 2024](https://arxiv.org/html/2402.13521v2) | Peer-reviewed ablation | HumanEval 164, MBPP 399, CodeChef 1,100 | Temp 0, fixed seed; repeats not stated | GPT-4 Turbo, Llama 3 70B | GPT-4 Turbo MBPP 69.67% → 82.45% with tests (87.71% with remediation); HumanEval 78.66% → 87.81% (93.30%); Llama 3 70B MBPP 46.37% → 75.94% (84.96%) |
| [Agentless](https://arxiv.org/html/2407.01489v2) | arXiv ablation | SWE-bench Lite, 300 | Not stated | GPT-4o | 25.67% → 27.00% (regression tests) → 32.00% (reproduction tests) |
| [Self-Debugging, ICLR 2024](https://arxiv.org/abs/2304.05128) | Peer-reviewed | TransCoder, MBPP, Spider | Not stated | Not given in abstract | Up to +12% with unit-test feedback; +2–3% on Spider without tests |
| [TDFlow](https://arxiv.org/html/2510.23761v1) | arXiv (EACL 2026 listing **not verified**) | SWE-bench Verified 455; Lite 278 | Not stated | GPT-4.1 on Lite | Human-written tests 94.3% vs LLM-generated tests 68.0% (paper intro says 69.8%); Lite 88.8% vs Agentless 61.0% |
| [Jain, martinfowler.com](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) | Practitioner experiment; guides and sensors bundled | 1 Java service, 178 hidden acceptance tests | 10 per model per arm (40) | GPT-6 Sol, GPT-6 Luna (Codex) | Luna 3/10 → 10/10; Sol 10/10 both ways at ~10.5x tokens and ~7x cost |
| [Chen et al.](https://arxiv.org/html/2602.07900v1) | arXiv, **null** | SWE-bench Verified 500; 4 models in interventions | Not stated (~USD 1,600 total) | gpt-5.2, gemini-3-pro, kimi-k2-thinking, deepseek-v3.2 | Encouraging agent tests: gpt-5.2 359 → 359 resolved, gemini-3-pro 371 → 366; 83.2% of outcomes unchanged |
| [TDAD](https://arxiv.org/html/2603.17973v2) | arXiv, **negative** | SWE-bench Verified, 100 | Temp 0; no significance tests | Qwen3-Coder 30B (4-bit) | TDD prompt raised regression rate 6.08% → 9.94%; resolution 31% → 31% |

## Related patterns and anti-patterns

[Deterministic Completion Gate](03-deterministic-completion-gate.md) enforces this one, [Protected Oracle](02-protected-oracle.md) keeps it honest, and [Independent, Execution-Grounded Review](10-independent-execution-grounded-review.md) adds a second opinion. The anti-patterns are the *Looks-Done Stop* and *Self-Graded Homework*, where the implementing agent writes the only tests that grade it.

## Maturity

**Grade: A (conditional).** Peer-reviewed controlled ablations (TGen, Self-Debugging) and the Agentless ablation show that *externally authored* executable checks raise success. The grade does not extend to agent-written tests, which have a measured null, or to the harness form itself (a command named in AGENTS.md), which no study has isolated on current models.
