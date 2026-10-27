#!/usr/bin/env python3
"""Detection check for pattern 01, Executable Done-Criteria.

Implements the Detection section of patterns/01-executable-done-criteria.md:

  A context file (AGENTS.md, CLAUDE.md, .github/copilot-instructions.md,
  .cursor/rules/*.mdc) contains at least one runnable verify command. The named
  command resolves in package.json, Makefile or pyproject.toml. Test files
  exist. For Copilot, copilot-setup-steps.yml is present.

Read-only: the script only reads files. It never runs, installs or imports
anything from the repo it checks.

Usage:
  python3 executable_done_criteria.py PATH/TO/REPO [--json]

Exit code: 0 when the pattern is detected, 1 when it is partial or absent,
2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", ".next",
             ".turbo", "vendor", "__pycache__", ".cache", "coverage"}

# Context files the catalog names, plus Copilot's path-specific instruction
# files (.github/instructions/*.instructions.md), which Copilot reads the same
# way as copilot-instructions.md.
CONTEXT_NAMES = {"AGENTS.md", "CLAUDE.md", "CLAUDE.local.md"}

# The catalog's pattern, verbatim.
CATALOG_RE = re.compile(
    r"pytest|go test|cargo (?:test|clippy)|(?:npm|pnpm|yarn) (?:run )?(?:test|lint|typecheck|build)"
    r"|tsc|ruff|mypy|eslint")

# Additions to the catalog's pattern, reported separately so the result says
# which rule matched. Each is a common runnable verify command the catalog
# pattern misses.
EXTENDED_RE = re.compile(
    r"manage\.py test"                                       # Django
    r"|turbo (?:run )?(?:test|lint|typecheck|build|check)"    # Turborepo
    r"|(?:npm|pnpm|yarn|bun) (?:run )?(?:check|verify|ci)\b"  # common script names
    r"|bun test|vitest|jest|make (?:test|check|lint|verify)\b"
    r"|go vet|cargo (?:check|fmt)|tox\b|nox\b")

# A whole command, so its script or target name can be resolved.
PKG_SCRIPT_RE = re.compile(
    r"\b(npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:-[-\w=]+\s+)*([\w:.@/-]+)")
TURBO_RE = re.compile(r"\bturbo\s+(?:run\s+)?([\w:.-]+)")
MAKE_RE = re.compile(r"\bmake\s+([\w.-]+)")

# Words after npm/pnpm/yarn that are subcommands, not script names.
PM_SUBCOMMANDS = {"install", "i", "add", "remove", "exec", "dlx", "x", "why",
                  "workspace", "workspaces", "--filter", "-r", "-w", "turbo"}

TEST_FILE_RE = re.compile(
    r"(^test_.*\.py$|_test\.py$|_test\.go$|\.(test|spec)\.[cm]?[jt]sx?$)")
TEST_DIR_NAMES = {"tests", "test", "__tests__", "spec"}


def walk(root: Path):
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = list(d.iterdir())
        except OSError:
            continue
        for p in entries:
            if p.is_symlink():
                continue
            if p.is_dir():
                if p.name not in SKIP_DIRS:
                    stack.append(p)
            elif p.is_file():
                yield p


def context_files(root: Path, files: list[Path]) -> list[Path]:
    out = []
    for p in files:
        rel = p.relative_to(root).as_posix()
        if p.name in CONTEXT_NAMES:
            out.append(p)
        elif rel == ".github/copilot-instructions.md":
            out.append(p)
        elif rel.startswith(".github/instructions/") and p.name.endswith(".instructions.md"):
            out.append(p)
        elif rel.startswith(".cursor/rules/") and p.suffix == ".mdc":
            out.append(p)
    return sorted(out)


def load_package_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return {}


def nearest(start: Path, root: Path, name: str) -> list[Path]:
    """Files called `name` from the context file's folder up to the root."""
    found = []
    d = start
    while True:
        cand = d / name
        if cand.is_file():
            found.append(cand)
        if d == root or root not in d.parents and d != root:
            break
        d = d.parent
    return found


def make_targets(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return set(re.findall(r"^([A-Za-z0-9_.-]+)\s*:(?!=)", text, re.M))


def pyproject_text(paths: list[Path]) -> str:
    chunks = []
    for p in paths:
        try:
            chunks.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    return "\n".join(chunks)


def resolve(cmd: str, ctx: Path, root: Path, all_pkg: list[Path]) -> tuple[bool, str]:
    """Return (resolved, where) for one matched command."""
    folder = ctx.parent
    pkgs = nearest(folder, root, "package.json")
    makefiles = nearest(folder, root, "Makefile")
    pyprojects = nearest(folder, root, "pyproject.toml")

    m = TURBO_RE.search(cmd)
    if m:
        task = m.group(1)
        turbo = root / "turbo.json"
        if turbo.is_file() and f'"{task}"' in turbo.read_text(errors="replace"):
            return True, f"turbo.json task `{task}`"
        for p in all_pkg:
            if task in (load_package_json(p).get("scripts") or {}):
                return True, f"{p.relative_to(root).as_posix()} script `{task}`"
        return False, f"turbo task `{task}` not found in turbo.json or package.json"

    m = PKG_SCRIPT_RE.search(cmd)
    if m and m.group(2) not in PM_SUBCOMMANDS:
        script = m.group(2)
        for p in pkgs:
            scripts = load_package_json(p).get("scripts") or {}
            if script in scripts:
                return True, f"{p.relative_to(root).as_posix()} script `{script}`"
        # `npm test` and `yarn test` are built-in aliases for the `test` script.
        return False, f"script `{script}` not in package.json between {folder.relative_to(root).as_posix() or '.'} and the root"

    m = MAKE_RE.search(cmd)
    if m:
        target = m.group(1)
        for mf in makefiles:
            if target in make_targets(mf):
                return True, f"{mf.relative_to(root).as_posix()} target `{target}`"
        return False, f"make target `{target}` not found"

    if "manage.py test" in cmd:
        hits = [p for p in root.rglob("manage.py") if not (SKIP_DIRS & set(p.parts))]
        if hits:
            return True, f"{hits[0].relative_to(root).as_posix()} exists (Django test runner)"
        return False, "manage.py not found"

    for tool in ("pytest", "ruff", "mypy", "tox", "nox"):
        if re.search(rf"\b{tool}\b", cmd):
            text = pyproject_text(pyprojects or [root / "pyproject.toml"])
            if f"[tool.{tool}" in text or re.search(rf"\b{tool}\b", text):
                return True, f"pyproject.toml configures or lists `{tool}`"
            return False, f"`{tool}` not found in pyproject.toml"

    for tool, configs in (("tsc", ("tsconfig.json",)),
                          ("eslint", ("eslint.config.js", "eslint.config.mjs", ".eslintrc.json",
                                      ".eslintrc.js", ".eslintrc.cjs", ".eslintrc")),
                          ("vitest", ("vitest.config.ts", "vitest.config.mts", "vitest.config.js")),
                          ("jest", ("jest.config.js", "jest.config.ts"))):
        if re.search(rf"\b{tool}\b", cmd):
            dep = "typescript" if tool == "tsc" else tool
            for p in pkgs:
                data = load_package_json(p)
                deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}
                if dep in deps:
                    return True, f"{p.relative_to(root).as_posix()} depends on `{dep}`"
            for c in configs:
                if (root / c).is_file() or (folder / c).is_file():
                    return True, f"`{c}` present"
            return False, f"no `{dep}` dependency or config found"

    if re.search(r"\bgo (test|vet)\b", cmd):
        return (root / "go.mod").is_file() or any(root.rglob("go.mod")), "go.mod"
    if re.search(r"\bcargo\b", cmd):
        return (root / "Cargo.toml").is_file(), "Cargo.toml"
    return False, "no rule to resolve this command"


def command_at(line: str, start: int) -> str:
    """The command around a match: inside backticks if any, else the rest of the line."""
    for m in re.finditer(r"`([^`]+)`", line):
        if m.start() <= start < m.end():
            return m.group(1).strip()
    return line[start:].strip().rstrip(".,;:)")


def check(root: Path) -> dict:
    files = list(walk(root))
    all_pkg = [p for p in files if p.name == "package.json"]
    ctx = context_files(root, files)
    found = []
    for c in ctx:
        try:
            lines = c.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for no, line in enumerate(lines, 1):
            seen = set()
            for rule, rx in (("catalog", CATALOG_RE), ("extended", EXTENDED_RE)):
                for m in rx.finditer(line):
                    cmd = command_at(line, m.start())
                    if cmd in seen:
                        continue
                    seen.add(cmd)
                    ok, where = resolve(cmd, c, root, all_pkg)
                    found.append({"file": c.relative_to(root).as_posix(), "line": no,
                                  "rule": rule, "command": cmd,
                                  "resolves": ok, "where": where})
    test_files = [p for p in files
                  if TEST_FILE_RE.search(p.name)
                  or (TEST_DIR_NAMES & set(p.relative_to(root).parts[:-1]) and p.suffix in {".py", ".ts", ".tsx", ".js", ".go"})]
    copilot_steps = (root / ".github/workflows/copilot-setup-steps.yml").is_file() or \
        (root / ".github/workflows/copilot-setup-steps.yaml").is_file()

    resolved = [f for f in found if f["resolves"]]
    if resolved and test_files:
        verdict = "detected"
    elif found:
        verdict = "partial"
    else:
        verdict = "absent"
    return {
        "repo": str(root),
        "context_files": [p.relative_to(root).as_posix() for p in ctx],
        "commands": found,
        "test_files": len(test_files),
        "copilot_setup_steps": copilot_steps,
        "verdict": verdict,
    }


def print_text(r: dict) -> None:
    print(f"Pattern 01, Executable Done-Criteria: {r['verdict'].upper()}")
    print(f"Context files ({len(r['context_files'])}): " + (", ".join(r["context_files"]) or "none"))
    if not r["commands"]:
        print("Verify commands: none found in context files")
    for f in r["commands"]:
        mark = "ok " if f["resolves"] else "-- "
        print(f"  {mark}{f['file']}:{f['line']}  [{f['rule']}]  {f['command']}")
        print(f"       {f['where']}")
    print(f"Test files: {r['test_files']}")
    print(f"Copilot setup steps (.github/workflows/copilot-setup-steps.yml): "
          f"{'present' if r['copilot_setup_steps'] else 'absent'}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    a = ap.parse_args(argv)
    root = a.repo.resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    r = check(root)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print_text(r)
    return 0 if r["verdict"] == "detected" else 1


if __name__ == "__main__":
    sys.exit(main())
