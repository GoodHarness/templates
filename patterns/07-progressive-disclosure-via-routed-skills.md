---
id: 07
name: Progressive Disclosure via Routed Skills
grade: "B (unreliable auto-triggering is A)"
graded: 2026-10-18
topic: "Skills"
evidence_models:
  - "GPT-5.2"
  - "Opus 4.5"
  - "Opus 4.6"
  - "Sonnet 4.5"
  - "Haiku 4.5"
  - "Gemini 3 Pro"
  - "Gemini 3 Flash"
  - "claude-sonnet-4-6"
catalog: v0
---

# Progressive Disclosure via Routed Skills

**Grade:** B (unreliable auto-triggering is A) · **Graded:** 18 Oct 2026 · **Topic:** Skills

Grades: A = controlled study or replicated measurement; B = vendor eval or single practitioner measurement with numbers; C = consistent recommendation, no measurement; D = proposed by few, untested. Not yet measured by Good Harness.

## Problem

Inlining every procedure costs tokens on every turn, but skills fail by never triggering. Claude Code users report matching skills being skipped ([#20986](https://github.com/anthropics/claude-code/issues/20986); [#19308](https://github.com/anthropics/claude-code/issues/19308)), and Vercel's skill was never invoked in 56% of eval cases ([Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)).

## Context

Skills suit vertical know-how that some tasks need, such as migrations, release steps or document formats. SkillsBench found the largest gains in procedural domains (Healthcare +51.9 pp, Manufacturing +41.9 pp) but only **+4.5 pp in software engineering** ([SkillsBench](https://arxiv.org/html/2602.12670v1)). Skills do poorly for knowledge almost every task needs; Vercel's always-on index reached 100% against 79% for an explicitly routed skill.

## Trade-offs

Unforced activation was 41% in Tessl's eval (929/2,286 tasks) ([Tessl](https://tessl.io/blog/a-proposed-framework-for-evaluating-skills-research-eng-blog)) and 50–55% in Spence's ([Spence](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals)). Forcing reaches 98–100%, but an LLM-eval hook fired falsely on 4 of 5 no-skill prompts. Listing budgets are finite: Claude Code allows 1% of context and drops the least-used descriptions ([skills docs](https://code.claude.com/docs/en/skills)), and Codex allows 2% or 8,000 characters ([Codex skills](https://learn.chatgpt.com/docs/build-skills)). Four or more skills gave only +5.9 pp. Of 31,132 marketplace skills, 26.1% had at least one vulnerability ([Agent Skills in the Wild](https://arxiv.org/html/2601.10338v1)).

## Solution

Use three disclosure levels: about 100 tokens of metadata, a body under 5,000 tokens and 500 lines, then files on demand ([agentskills.io](https://agentskills.io/specification)). Add routing, because triggering is the weak link: name the skill in AGENTS.md ("when X, use skill Y"), which took Vercel from 53% to 79%, or use a forced-eval hook.

## Implementation per agent

| Agent | Implementation |
|---|---|
| Claude Code | `.claude/skills/<name>/SKILL.md` with `description`, `when_to_use`, `paths`, `disable-model-invocation`, `context: fork`. `/skill-doctor` reports cost, and `claude plugin eval` has a `tool_used: Skill` grader ([docs](https://code.claude.com/docs/en/skills)). |
| Cursor | `.cursor/skills/` or `.agents/skills/` (also reads `.claude/skills/`), with `paths` and `disable-model-invocation` ([docs](https://cursor.com/docs/context/skills)). |
| Codex | `.agents/skills/`, invoked implicitly or with `$skill`. `allow_implicit_invocation` lives in `agents/openai.yaml`; budget is `skills.max_context_tokens` ([docs](https://learn.chatgpt.com/docs/build-skills)). |
| GitHub Copilot | `.github/skills/`, `.claude/skills/` or `.agents/skills/` in the cloud agent, code review, CLI and VS Code. GitHub does not verify skills; inspect them with `gh skill preview` ([docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills)). |

## Detection

Glob `{.claude,.agents,.cursor,.github,.codex}/skills/*/SKILL.md` and validate frontmatter (`skills-ref validate` or `claude plugin validate`). Check that each description contains a "Use when" trigger, the body is 500 lines or fewer and the name matches its folder. Flag more than about 20 skills and any `scripts/` for review. Check whether AGENTS.md or CLAUDE.md routes to skills by name.

## Prediction

Success rises in the skill's domain *only if activation is verified*, and always-on tokens fall compared with inlining. Expect 40–60% unforced activation unless the skill is routed or forced.

## Evidence

| Source | Type | Sample / tasks | Runs | Models | Effect |
|---|---|---|---|---|---|
| [SkillsBench](https://arxiv.org/html/2602.12670v1) | arXiv | 84 tasks (abstract says 86), 11 domains, 3 harnesses; 7,308 trajectories | ~5 per task | GPT-5.2, Opus 4.5/4.6, Sonnet 4.5, Haiku 4.5, Gemini 3 Pro/Flash | Curated +16.2 pp; self-generated about −1.3 pp; software engineering +4.5 pp; 16/84 tasks negative; "comprehensive" skills −2.9 pp |
| [Tessl](https://tessl.io/blog/a-proposed-framework-for-evaluating-skills-research-eng-blog) | Vendor eval | ~500 skills, up to 5 tasks each | Not stated | claude-sonnet-4-6, Haiku 4.5 | ~20% absolute accuracy gain; activation 41% unforced vs 98% forced (2,286 tasks) |
| [Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) | Vendor eval; **negative for skills vs always-on** | Not stated | Not stated | Not stated | Default skill +0 pp; with explicit instructions +26 pp; AGENTS.md index +47 pp |
| [Spence](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals) | Practitioner experiment | 4 skills, 22 prompts | 2 | Sonnet 4.5 | Activation 50–55% baseline; 100% with forced-eval hooks |

## Related patterns and anti-patterns

[Lean Root Context File](05-lean-root-context-file.md) holds horizontal knowledge. *Explicitly invoked workflows* (a candidate, not yet in the catalog) are the same artifact with model invocation off, and hooks hold must-run rules. The anti-pattern is *Skill Hoarding*.

## Maturity

**Grade: B.** A controlled arXiv study and a large vendor eval show uplift *when skills load*, and three independent measurements replicate unreliable auto-triggering (an A-grade sub-finding). The only head-to-head against always-on context points the other way and has undisclosed n.
