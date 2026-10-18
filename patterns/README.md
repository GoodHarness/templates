# Good Harness pattern catalog (v0)

Fourteen harness patterns for coding agents, each written as a pattern (problem, context, trade-offs, solution, implementation per agent, detection, prediction, evidence, related patterns) with an evidence grade dated 18 Oct 2026. Grades come from published studies, vendor evals and practitioner reports. Good Harness has not yet measured any of them; each grade changes as our own paired multi-run evals land.

**Grades:** A = controlled study or replicated measurement · B = vendor eval or single practitioner measurement with numbers · C = consistent recommendation, no measurement · D = proposed by few, untested. Where the problem and the fix have different evidence, the grade is split.

| # | Pattern | Topic | Grade |
|---|---|---|---|
| 1 | [Executable Done-Criteria](01-executable-done-criteria.md) | Workflows, context files | A (conditional on externally written checks) |
| 2 | [Protected Oracle](02-protected-oracle.md) | Permissions, hooks | A for the problem and benchmark mitigations; C for repo enforcement |
| 3 | [Deterministic Completion Gate](03-deterministic-completion-gate.md) | Hooks | C |
| 4 | [Teaching Sensors](04-teaching-sensors.md) | Hooks, linters | B |
| 5 | [Lean Root Context File](05-lean-root-context-file.md) | Context files | B (the generated-file downside is A) |
| 6 | [Tool Budget](06-tool-budget.md) | MCP | A for mechanism; B for coding-task success |
| 7 | [Progressive Disclosure via Routed Skills](07-progressive-disclosure-via-routed-skills.md) | Skills | B (unreliable auto-triggering is A) |
| 8 | [Read-Only Sub-agents](08-read-only-sub-agents.md) | Sub-agents | B |
| 9 | [Plan Gate](09-plan-gate.md) | Workflows | B (agent-side planning for weaker models A; human approval C) |
| 10 | [Independent, Execution-Grounded Review](10-independent-execution-grounded-review.md) | Workflows, sub-agents | B (self-review unreliability A) |
| 11 | [Small Units with Checkpoints](11-small-units-with-checkpoints.md) | Workflows | B |
| 12 | [Sandboxed Autonomy](12-sandboxed-autonomy.md) | Permissions | B for friction; C for harm |
| 13 | [Untrusted-Input Containment](13-untrusted-input-containment.md) | Permissions, MCP | C (problem A) |
| 14 | [Paired Multi-Run Evaluation](14-paired-multi-run-evaluation.md) | Measurement | A |

## Candidates not yet catalogued

These candidates surfaced in our research but have thinner evidence or overlap with the entries above. Each may be promoted to a full entry later.

| Candidate | Grade | Basis |
|---|---|---|
| Agent-computer interface shaping | A, with 2024 models and unstated runs | SWE-agent ablations: no edit command −7.7 pp, full-file viewer −5.3 pp, iterative search −6.0 pp ([SWE-agent](https://arxiv.org/html/2405.15793v3)) |
| In-session context hygiene | A for effect; B for practice | Last-5 observations 18.0% vs full history 15.0% ([SWE-agent](https://arxiv.org/html/2405.15793v3)); context rot across 18 models ([Chroma](https://www.trychroma.com/research/context-rot)) |
| Failure-driven harness improvement | B (some sources would put it at C) | +13.7 pp TB 2.0, no run count ([LangChain](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)); Self-Harness gains on 9 of 9 pairs, abstract only ([arXiv](https://arxiv.org/abs/2606.09498)); its maxim is "engineer a solution such that the agent never makes that mistake again" ([Hashimoto](https://mitchellh.com/writing/my-ai-adoption-journey)) |
| Advisor escalation | B | +2.7 pp on SWE-bench Multilingual over 5 trials of 300, at 11.9% lower cost ([Anthropic](https://claude.com/blog/the-advisor-strategy)) |
| Best-of-N with filtered selection | B | Opus 4 72.5% → 79.4%, Sonnet 4 72.7% → 80.2%; N not disclosed ([Anthropic](https://www.anthropic.com/news/claude-4)) |
| Per-model harness profiles | B | tau2 subset 33% → 53% and 43% → 53%, run count not stated ([LangChain](https://www.langchain.com/blog/tuning-deep-agents-different-models)) |
| Load-bearing audit on model upgrade | B | Framework gap 19.4 → 3.8 → 0.9 pp ([Mehtiyev](https://arxiv.org/pdf/2604.02547)); ">80%" of system prompt cut with no measurable loss, vendor claim without n ([Claude blog](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)) |
| Loop and stagnation detection | B in notes; intervention never isolated | Step repetition 15.7% ([MAST](https://arxiv.org/html/2503.13657v3)); only tested inside LangChain's bundle |
| Scoped context loading | C | Vendor docs only; on-demand vs always-on null at n=45 ([Khatri](https://www.alphaxiv.org/abs/2607.27250)) |
| One canonical instruction file | C | >60,000 adopting projects is a claim with no method ([Linux Foundation](https://linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)) |
| Context file as code | C (automated path linting D) | 24 of 100 top files never edited after creation ([dos Santos](https://arxiv.org/html/2606.15828v5)) |
| Least privilege and credential isolation | C (B-grade negative for deny lists) | Regex guards leaked, e.g. opencode 16/16 ([Adversa](https://adversa.ai/blog/opensource-ai-coding-agents-shell-injection-vulnerability/)) |
| Reproducible agent environment | C | Agents set up only 6.69% of Python repos unaided ([EnvBench](https://arxiv.org/abs/2503.14443)); no before/after for setup files |
| Explicitly invoked workflows | C | Forced activation 98% ([Tessl](https://tessl.io/blog/a-proposed-framework-for-evaluating-skills-research-eng-blog)); no outcome data |
| Merge-ready PR shaping; completion-claim audit; durable progress artifacts | C | Problems measured at scale ([Ehsani](https://arxiv.org/html/2601.15195v1); [Zhao](https://www.alphaxiv.org/abs/2607.09510)); fixes untested |
| TDD prompting; drift-sweeping agents; budget signals; early-trajectory monitoring | D (TDD negative on small models) | Negative regression result ([TDAD](https://arxiv.org/html/2603.17973v2)); OpenAI anecdote ([OpenAI](https://openai.com/index/harness-engineering/)); untested bundle parts |

## Open verification items

These details could not be confirmed from primary sources on 18 Oct 2026. Pattern files keep the same flags.

| Item | Status in the research | Link |
|---|---|---|
| Tang et al. per-symptom shares and CLI vs IDE split (49.49% vs 32.26%) | Secondary summary only, not verified | [secondary](https://codex.danielvaughan.com/2026/07/01/coding-agent-misalignment-20574-sessions-codex-cli-constraint-enforcement-self-reporting-defence/) |
| MAST category totals | Researcher's sums, not paper figures | [MAST](https://arxiv.org/html/2503.13657v3) |
| Terminus 2 with Opus 4.6 at 62.9% → 74.4% | X post via blog, unverified | [secondary](https://codex.danielvaughan.com/2026/04/09/harness-performance-terminal-bench/) |
| Lulla venue (ICSE JAWs) and TDFlow venue (EACL 2026) | Not verified on arXiv | [Osmani](https://addyosmani.com/blog/agents-md/); [ACL preview](https://preview.aclanthology.org/ingest-eacl/2026.eacl-long.70) |
| Claude Code #40117 closure and #6235 vote counts | Secondary sources | [pydevtools](https://pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/); [thepromptshelf](https://thepromptshelf.dev/blog/claude-code-6235-agents-md-closed-completed-2026/) |
| Claude Code native AGENTS.md fallback | A third-party post says it never shipped; official docs say it did. Trust the docs | [memory docs](https://code.claude.com/docs/en/memory) |
| Codex: path-level write deny (PreToolUse covers `apply_patch` edits, confirmed 18 Oct; matching is by tool name only), `review_model`, launch-era check behaviour | Not verified | [Codex hooks](https://learn.chatgpt.com/docs/hooks) |
| Cursor: file-path field in `preToolUse` Write input (the hook fires for Write, confirmed 18 Oct); `.cursor/commands/` path; 40–50 tool warning | Not confirmed | [Cursor hooks](https://cursor.com/docs/agent/hooks) |
| Copilot: `agentStop` `reason` field (`decision: "block"` confirmed 18 Oct); Copilot CLI MCP path and prompt-file support | Not confirmed | [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference) |
| Kiro/Q outage (FT), Antigravity (Register), Gemini CLI advisory, Codex docker X post, PocketOS token source | Taken from tracker summaries, not read directly | [Oso](https://www.osohq.com/developers/ai-agents-gone-rogue) |
| CMU spec-driven development paper | Abstract and HTML versions differ; verify before citing | [alphaXiv](https://www.alphaxiv.org/abs/2608.25202) |
| Nakashima no-explicit-reason share | Sources give 69.0% for agent PRs and 67.9% for all rejections; confirm which | [arXiv](https://arxiv.org/html/2602.04226v1) |
| Jarmak entry format and grading scale | Not readable from the abstract | [arXiv](https://arxiv.org/abs/2608.13867) |
