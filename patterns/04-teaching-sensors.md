---
id: 04
name: Teaching Sensors
grade: "B"
graded: 2026-10-18
topic: "Hooks, linters"
evidence_models:
  - "GPT-4 Turbo"
  - "GPT-4o"
catalog: v0
---

# Teaching Sensors

**Grade:** B · **Graded:** 18 Oct 2026 · **Topic:** Hooks, linters

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Agents produce code that passes tests but breaks conventions, security hygiene or architecture, and prose rules leave this unenforced. On 470 prompts, more than 40% of GPT-4o outputs had Bandit security findings and more than 80% had Pylint convention findings before feedback ([Blyth et al.](https://arxiv.org/html/2508.14419v1)). OpenAI says its team spent every Friday, about 20% of the week, cleaning up agent output before automating rules (vendor claim) ([OpenAI](https://openai.com/index/harness-engineering/)). 62% of top-100 context files put lint rules in prose ("Lint Leakage") ([dos Santos et al.](https://arxiv.org/html/2606.15828v5)).

## Context

The pattern applies to stable, mechanically checkable rules: layer direction, import boundaries, naming, structured logging, secrets. It is weak for design judgment. Böckeler says neither computational nor inferential sensors reliably catch misdiagnosis or over-engineering ([Böckeler](https://martinfowler.com/articles/harness-engineering.html)). Cursor's in-IDE lint loop does not run in the CLI or Cloud Agents ([forum](https://forum.cursor.com/t/does-agents-iterate-on-lint-errors-work-with-custom-third-party-lsp-servers-or-only-built-in-linters/168705)).

## Trade-offs

Someone writes and maintains the rules; Factory keeps "dozens" (vendor claim) ([Factory](https://factory.com/news/using-linters-to-direct-agents)). Refinement causes regressions: about 5% of iterations introduced new security flaws ([Blyth et al.](https://arxiv.org/html/2508.14419v1)). Lint-fixing loops crowding out the task is reported only in forum anecdotes and is unmeasured. A silent sensor can mean quality or weak detection ([Böckeler](https://martinfowler.com/articles/harness-engineering.html)).

## Solution

Encode each recurring mistake as a deterministic check: a custom lint rule, an architecture test (ArchUnit, dependency-cruiser, import rules) or a semgrep rule. Write the error message as the fix instruction, run it in the agent loop through a post-edit hook, and back it with CI. OpenAI says it writes lint messages to inject remediation into agent context (vendor claim) ([OpenAI](https://openai.com/index/harness-engineering/)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `PostToolUse` hook with matcher `Edit|Write` runs the linter; exit 2 shows stderr to Claude; `continueOnBlock` feeds the reason back ([hooks guide](https://code.claude.com/docs/en/hooks-guide)). LSP plugins detect errors after edits ([best practices](https://code.claude.com/docs/en/best-practices)). |
| Cursor | The built-in lint tool consumes any LSP diagnostics, including custom servers, in the IDE only. `afterFileEdit` can run a linter but cannot block ([forum](https://forum.cursor.com/t/does-agents-iterate-on-lint-errors-work-with-custom-third-party-lsp-servers-or-only-built-in-linters/168705); [hooks](https://cursor.com/docs/agent/hooks)). |
| Codex | A `PostToolUse` hook with `decision: "block"` replaces the tool result with feedback ([hooks](https://learn.chatgpt.com/docs/hooks)). |
| GitHub Copilot | The project linter runs as a default validation tool (vendor claim); `postToolUse` hooks are also available ([changelog](https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/); [reference](https://docs.github.com/en/copilot/reference/hooks-reference)). |

## Detection

Repo-local rules exist: a local ESLint plugin, `.semgrep.yml`, `.dependency-cruiser.*`, an importlinter config, ArchUnit tests or a custom golangci linter. Rule messages contain fix wording ("use", "instead", "see docs/"). A post-edit hook runs the linter, and CI runs the same rules.

## Prediction

Convention, architecture and security violations reaching review go down, and review rework goes down. Each edit adds a little latency. Functional success changes little: in Blyth et al., error-type issues moved only from about 20–21% to 14–16%.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [SWE-agent, NeurIPS 2024](https://arxiv.org/html/2405.15793v3) | Peer-reviewed ablation | SWE-bench Lite, 300 | Not stated | GPT-4 Turbo | Lint-gated edits 18.0% vs 15.0% without linting (inside today's 2.2–6.0 pp noise band) |
| [Blyth et al.](https://arxiv.org/html/2508.14419v1) | arXiv | 470 PythonSecurityEval prompts; up to 10 iterations | Not stated | GPT-4o | Security >40% → 13%; readability >80% → 11%; reliability >50% → 11%; functional ~35.7–38.2% → 46.6–47.8%; ~5% of iterations added new flaws |
| None | — | — | — | — | **No study compares remediation-style vs plain lint messages, or measures architecture rules** |

## Related patterns and anti-patterns

[Deterministic Completion Gate](03-deterministic-completion-gate.md) is where the sensor runs. Lint rules should move out of [Lean Root Context File](05-lean-root-context-file.md)'s context file into sensors. The anti-patterns are *Prose-Only Conventions* and the *Cryptic Sensor*, which says what failed but not how to fix it.

## Maturity

**Grade: B.** Two measurements show lint and static feedback improving output (one peer-reviewed single-model ablation, one arXiv function-level study). The pattern's distinctive claims, error messages as instructions and enforced architecture rules, rest only on vendor and practitioner reports without numbers.
