# Detection checks

Each script checks one repo for one catalog pattern. It reads files only: it never runs, installs or imports anything from the repo it checks.

| Script | Pattern | What it looks for |
| --- | --- | --- |
| `executable_done_criteria.py` | [01 · Executable Done-Criteria](../patterns/01-executable-done-criteria.md) | A runnable verify command in a context file, whether that command resolves in the repo, and whether test files exist |

## Run it

```
python3 detect/executable_done_criteria.py path/to/your/repo
python3 detect/executable_done_criteria.py path/to/your/repo --json
```

Python 3.9 or later, standard library only. Exit code 0 means detected, 1 means partial or absent.

## How 01 is checked

This script follows the Detection section of the pattern file.

- **Context files:**
  - `AGENTS.md`, `CLAUDE.md` and `CLAUDE.local.md`, at any depth;
  - `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md`;
  - `.cursor/rules/*.mdc`.
- **Verify commands:** only text inside inline backticks or a fenced code block counts. A tool named in prose ("we use ruff") is not a runnable command. Two rules are applied, and each match says which rule found it.
  - `catalog` is the pattern file's own pattern, with word edges added so `tsconfig` or `vitest.config.ts` don't count.
  - `extended` adds common commands it misses: `manage.py test`, `turbo run test`, `vitest`, `jest`, `make test` and similar.
- **Resolves:**
  - an npm, pnpm, yarn or bun script is found in a `package.json` between the context file's folder and the repo root, or the name is a tool binary such as `tsc` and its package is a dependency;
  - a turbo task is found in `turbo.json`;
  - a make target is found in a `Makefile`;
  - pytest, ruff or mypy appears in `pyproject.toml`;
  - tsc, eslint, vitest or jest is a dependency or has a config file.
- **Test files:** files named like `test_*.py`, `*_test.py`, `*_test.go` or `*.test.ts`, `*.spec.ts` and their `.js`/`.tsx` variants, or source files inside a `tests/` or `__tests__/` folder.
- **Copilot:** whether `.github/workflows/copilot-setup-steps.yml` exists. This is reported on its own line and doesn't change the verdict.

**Verdicts:**
- `detected`: at least one resolved command, and test files exist.
- `partial`: a command is named but doesn't resolve, or no test files were found.
- `absent`: no verify command in any context file.

## What it does not check

- **Evidence before "done":** whether the context file asks the agent to show the command and its output before it says it's done. That is wording, not syntax, so read the file.
- **Skills:** commands named only in a skill (for example `.claude/skills/*/SKILL.md`). The pattern file counts context files.
- **Whether the check passes, or is any good:** a named command that runs a thin suite still counts as detected. The pattern's grade holds only for checks written outside the agent; see the pattern file.
