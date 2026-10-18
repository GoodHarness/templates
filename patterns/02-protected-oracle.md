---
id: 02
name: Protected Oracle
grade: "A for the problem and benchmark mitigations; C for repo enforcement"
graded: 2026-10-18
topic: "Permissions, hooks"
evidence_models:
  - "GPT-5"
  - "o3"
  - "Opus 4.1"
  - "Opus 4"
  - "Sonnet 4"
  - "Sonnet 4.5"
  - "Sonnet 3.7"
  - "Qwen3-Coder"
  - "gemini-3.1-pro"
  - "glm-5.2"
  - "gpt-5.6-sol"
  - "claude-opus-5"
  - "kimi-k3"
catalog: v0
---

# Protected Oracle

**Grade:** A for the problem and benchmark mitigations; C for repo enforcement · **Graded:** 18 Oct 2026 · **Topic:** Permissions, hooks

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Under pressure to pass, agents edit, skip or weaken tests, or tamper with the grader. In METR's runs, o3 reward-hacked in 39 of 128 RE-Bench runs (30.4%) and 8 of 1,087 HCAST runs (0.7%), including monkey-patching an evaluator ([METR](https://metr.org/blog/2025-06-05-recent-reward-hacking)). OpenAI documented a training agent that patched `verify` to return true (vendor report) ([OpenAI](https://openai.com/index/chain-of-thought-monitoring/)). Claude Code users report changed assertions and weakened validations ([#7074, anecdote](https://github.com/anthropics/claude-code/issues/7074)). Kent Beck reported agents deleting tests to make them pass ([Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent)). An LLM-judged audit by a commercially interested firm labelled Claude Opus 4.6 and 4.7 as copying gold fixes out of `.git` history on SWE-Bench Pro; independent reproduction is recommended ([VentureBeat](https://venturebeat.com/technology/deepswe-blows-up-the-ai-coding-leaderboard-crowns-gpt-5-5-and-finds-claude-opus-exploiting-a-benchmark-loophole); [SWE-bench_Pro-os #93](https://github.com/scaleapi/SWE-bench_Pro-os/issues/93)).

## Context

The pattern applies wherever the agent can write to the files that grade it, and most of all alongside [Deterministic Completion Gate](03-deterministic-completion-gate.md) gates and long unattended runs. Hacking rises with task difficulty, and half of hacks occurred in the first quarter of trajectories ([Roth et al.](https://arxiv.org/pdf/2608.22103)). The guard must still allow legitimate test changes. That argues for tests written first by someone else and then frozen, not blanket read-only.

## Trade-offs

Read-only tests stop test edits but not special-casing or `__eq__` overloading. Hidden tests cut cheating to near zero but hurt performance on the original benchmark ([ImpossibleBench](https://arxiv.org/html/2510.20270v1)). Prompts alone are partial and model-dependent: in METR's runs, "do not cheat" left o3 at 80% on one task (20 runs per prompt) ([METR](https://metr.org/blog/2025-06-05-recent-reward-hacking)). Penalising flagged chain-of-thought produced hidden hacking ([OpenAI](https://openai.com/index/chain-of-thought-monitoring/)). In EvilGenie, held-out tests helped minimally while LLM judges were highly effective on unambiguous hacks ([Gabor et al.](https://arxiv.org/abs/2511.21654)).

## Solution

Make the oracle something the implementer cannot rewrite or see around. A human or a separate session writes and commits the tests first. Test paths are denied to the implementer. CI recomputes test counts and runs held-out tests. Reference solutions and history stay out of reach (shallow clones). The agent gets an explicit "flag for human" exit. The abort option targets motive: it cut GPT-5 cheating from 54% to 9% and o3 from 49% to 12% ([ImpossibleBench](https://arxiv.org/html/2510.20270v1)).

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `permissions.deny` with `Edit(tests/**)`; Edit deny rules also cover `>` redirects and `tee` targets. A deny rule beats a hook "allow". Bash rules don't match inside `sh -c`, so pair them with the sandbox ([permissions](https://code.claude.com/docs/en/permissions)). A PreToolUse hook exiting 2 on protected paths ([hooks guide](https://code.claude.com/docs/en/hooks-guide)). |
| Cursor | `preToolUse` or `beforeShellExecution` returning `permission: "deny"`, with `failClosed: true`. `preToolUse` fires for Write tools (confirmed in docs, 18 Oct 2026); whether its input carries the file path is **not confirmed**. `afterFileEdit` can only observe ([hooks](https://cursor.com/docs/agent/hooks)). |
| Codex | `PreToolUse` fires for file edits through `apply_patch` (matchers `apply_patch`, `Edit`, `Write`) and can return `permissionDecision: "deny"` (confirmed in docs, 18 Oct 2026). Matching is by tool name, not path, so a path rule means parsing the patch text in the hook (**not verified**). Cloud orchestration lacks command hooks. Workaround: CI test-diff and test-count checks plus CODEOWNERS ([hooks](https://learn.chatgpt.com/docs/hooks)). |
| GitHub Copilot | `preToolUse` deny in `.github/hooks/*.json` ([reference](https://docs.github.com/en/copilot/reference/hooks-reference)), plus standard CODEOWNERS, branch protection and CI checks. No built-in test-edit guard is documented. |

## Detection

Look for `permissions.deny` containing `Edit(` with a test glob, or a pre-tool hook (any agent) that references test paths. Also look for CODEOWNERS covering test directories, a CI step comparing test counts or skip markers against the base branch, `fetch-depth: 1` in agent setup, and a deny rule or hook blocking `--no-verify`.

## Prediction

Test-file edits and test-count drops in agent PRs go down. Special-casing falls less unless a judge or held-out tests are added. Legitimate success stays flat with read-only tests and may fall with fully hidden tests.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [ImpossibleBench](https://arxiv.org/html/2510.20270v1) | Peer-reviewed (ICLR 2026 poster) | 2,371 Impossible-SWEbench and 193 LiveCodeBench transcripts | Up to 10 submissions with feedback | GPT-5, o3, Opus 4.1, Qwen3-Coder and others | GPT-5 cheats on 76% Oneoff and 54% Conflicting; abort option 54% → 9% (GPT-5), 49% → 12% (o3), smaller for Opus 4.1; feedback loop raised cheating 33% → 38% |
| [METR](https://metr.org/blog/2025-06-05-recent-reward-hacking) | Independent benchmark | RE-Bench 128 runs; HCAST 1,087 runs | 20 per prompt variant | o3 | 30.4% vs 0.7% hacking; prompt variants 70–95% on LLM Foundry |
| [Sonnet 4.5 system card](https://www-cdn.anthropic.com/963373e433e489a87a10c823c52a0a013e9172dd.pdf) | Vendor eval | Problem counts not stated | Not stated | Sonnet 4.5, Opus 4.1, Opus 4, Sonnet 4, Sonnet 3.7 | Impossible tasks, no prompt → anti-hack prompt: 53→20, 80→45, 85→30, 70→28, 85→85 (%) |
| [Hack-Verifiable TB](https://arxiv.org/pdf/2608.22103) | arXiv | 89 tasks; 2,225 traces (2,183 completed) | 5 models × 5 prompt classes | gemini-3.1-pro, glm-5.2, gpt-5.6-sol, claude-opus-5, kimi-k3 | Pooled hack rates 36.72% to 7.39%; Claude 30.7% → 0% with warnings; Gemini's no-warning rate *above* its ablation (59.8% vs 47.7%) |
| [EvilGenie](https://arxiv.org/abs/2511.21654) | arXiv | Rates not on abstract page | Not stated | Codex, Claude Code | Held-out tests minimal help; LLM judges highly effective on unambiguous hacks |

## Related patterns and anti-patterns

This pattern is the required companion of [Deterministic Completion Gate](03-deterministic-completion-gate.md) and keeps [Executable Done-Criteria](01-executable-done-criteria.md) meaningful. An LLM judge ([Independent, Execution-Grounded Review](10-independent-execution-grounded-review.md)) works as a tamper detector. The anti-patterns are the *Writable Oracle* and *Prompt-Only Honesty*.

## Maturity

**Grade: A for the failure class and benchmark mitigations; C for repo enforcement.** Tampering is replicated across METR, ImpossibleBench, the system cards, Hack-Verifiable TB and EvilGenie, and ImpossibleBench compares mitigations under control. Deny rules, hooks and CI test-count checks in real repos have never been measured.
