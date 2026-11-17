#!/usr/bin/env bash
# check-agent-config.sh - Good Harness read-only check (Recommended, not a vendor tool)
#
# Lists coding-agent config files that are tracked in a git repo now and that
# ever appeared in its history (all refs), flags local-only files that should
# never be tracked, and flags credential-looking text in added lines.
# Optionally runs gitleaks (default rules + one extra agent-config rule) and
# TruffleHog (no live verification) over the same paths if they are installed.
#
# Read-only: it never modifies the repo, the index, refs or config. Scanner
# reports go to a temp dir outside the repo and are deleted on exit.
# Matches are printed redacted. Run it only on repositories you own.
#
# Usage:  bash check-agent-config.sh [path-to-repo]
# Exit:   0 = nothing flagged, 1 = something flagged, 2 = not a git repo

set -uo pipefail
REPO="${1:-.}"
cd "$REPO" 2>/dev/null || { echo "cannot cd to $REPO"; exit 2; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git work tree: $REPO"; exit 2; }
cd "$(git rev-parse --show-toplevel)"

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FLAGGED=0

# Agent config paths (glob pathspecs, so nested copies are found too)
PATHSPECS=(
  ':(glob)**/.claude/**'          # Claude Code project dir (settings, rules, skills, agents)
  ':(glob)**/CLAUDE.md'  ':(glob)**/CLAUDE.local.md'
  ':(glob)**/.mcp.json'           # Claude Code project MCP; also read by Copilot CLI / VS Code
  ':(glob)**/.cursor/**'          # Cursor (mcp.json, permissions.json, cli.json, rules, skills)
  ':(glob)**/.codex/**'           # Codex project layer (config.toml, rules/*.rules)
  ':(glob)**/.agents/**'          # shared skills dir read by Cursor / Copilot CLI
  ':(glob)**/AGENTS.md'  ':(glob)**/AGENTS.override.md'
  ':(glob)**/.vscode/mcp.json'  ':(glob)**/.vscode/settings.json'
  ':(glob).github/copilot/**'  ':(glob).github/copilot-instructions.md'  ':(glob).github/mcp.json'
  ':(glob)**/.gemini/**'  ':(glob)**/GEMINI.md'
)
# Files vendors document as personal/local-only, plus credential stores
LOCAL_ONLY_RE='(^|/)(\.claude/settings\.local\.json|CLAUDE\.local\.md|\.github/copilot/settings\.local\.json|\.codex/auth\.json)$'

echo "== 1. Agent config files tracked now =="
git ls-files -- "${PATHSPECS[@]}" | sort > "$TMP/now.txt"
if [ -s "$TMP/now.txt" ]; then sed 's/^/  /' "$TMP/now.txt"; else echo "  (none)"; fi

echo; echo "== 2. Agent config paths that ever appeared in history (all refs) =="
git log --all --format= --name-only -- "${PATHSPECS[@]}" | sed '/^$/d' | sort -u > "$TMP/hist.txt"
if [ -s "$TMP/hist.txt" ]; then
  while IFS= read -r p; do
    if grep -qxF -- "$p" "$TMP/now.txt"; then echo "  $p"; else echo "  $p   <- not tracked now, still in history"; fi
  done < "$TMP/hist.txt"
else echo "  (none)"; fi

echo; echo "== 3. Local-only files that are (or were) tracked =="
if grep -E "$LOCAL_ONLY_RE" "$TMP/hist.txt" > "$TMP/local.txt"; then
  while IFS= read -r p; do
    echo "  FLAG $p"
    git log --all --format='       %h %ad %s' --date=short -- "$p" | head -5
  done < "$TMP/local.txt"; FLAGGED=1
else echo "  (none)"; fi

echo; echo "== 4. Are local-only files ignored by THIS repo? (git check-ignore) =="
for p in .claude/settings.local.json CLAUDE.local.md .github/copilot/settings.local.json; do
  src="$(git check-ignore -v --no-index -- "$p" 2>/dev/null | cut -f1)"
  case "$src" in
    "") echo "  $p: NOT ignored";;
    .gitignore:*|*/.gitignore:*) echo "  $p: ignored by repo ($src)";;
    *) echo "  $p: ignored only by $src (global or info/exclude: does not travel with the repo)";;
  esac
done

echo; echo "== 5. Credential-looking text in added lines (all history, redacted) =="
# Heuristics only. Values written as ${VAR} / $VAR / ${env:VAR} / ${input:id} are skipped.
# (Python is used because some awk builds mis-handle regex intervals such as {8,}.)
if command -v python3 >/dev/null 2>&1; then
git log --all -p --no-color --no-ext-diff --format='@@C %h' -- "${PATHSPECS[@]}" 2>/dev/null |
python3 -I -c '
import re, sys
V = r"[^\s\"\x27\\)$@{}]"                      # one value character (stops at quotes, ), $, @, braces)
RULES = [
  ("known-token-prefix", r"(?i)\b(?:ghp_|gho_|ghs_|github_pat_|xox[bp]-|sk-[a-z0-9_-]{16}|AKIA[0-9A-Z]{16})" + V + r"*"),
  ("auth-header",        r"(?i)authorization:\s*(?:bearer|basic|token)\s+(" + V + r"{8,})"),
  ("uri-credentials",    r"://[^/\s:@\"]+:([^@\s$\"{}]{3,})@"),
  ("attached -p value",  r"(?:^|[\s(\"])-p([^\s$\"\x27\\){}-]" + V + r"{5,})"),
  ("sshpass -p",         r"(?i)sshpass\s+-p\s*(" + V + r"+)"),
  ("secret-flag",        r"(?i)--?(?:password|passwd|pass|pwd|token|secret|api-?key|apikey)[ =](" + V + r"{6,})"),
  ("env-assignment",     r"(?i)(?:^|[^a-z0-9_])[a-z0-9_]*(?:key|token|secret|passw(?:or)?d|pwd)[a-z0-9_]*=(" + V + r"{8,})"),
  ("json-literal",       r"(?i)\"[a-z0-9_-]*(?:key|token|secret|passw(?:or)?d|pwd|authorization)[a-z0-9_-]*\"\s*:\s*\"([^\"$]{8,})\""),
  ("user:pass",          r"\s-u\s+[^\s:$\"]+:(" + V + r"{3,})"),
]
RULES = [(n, re.compile(r)) for n, r in RULES]
def mask(v): return (v[:3] + "***") if len(v) > 3 else "***"
c = f = ""; n = 0
for raw in sys.stdin:
    line = raw.rstrip("\n")
    if line.startswith("@@C "): c = line[4:]; continue
    if line.startswith("+++ "): f = line[6:] if line.startswith("+++ b/") else ""; continue
    if not line.startswith("+"): continue
    text = line[1:]; hits = []; shown = text
    for name, rx in RULES:
        for m in rx.finditer(text):
            hits.append(name)
            val = m.group(1) if m.groups() else m.group(0)
            shown = shown.replace(val, mask(val))
    if hits:
        n += 1
        shown = shown.strip()
        rules = ", ".join(sorted(set(hits)))
        print(f"  FLAG {c} {f} [{rules}] {shown[:160]}")
print("  (none)" if not n else f"  {n} line(s) flagged")
sys.exit(1 if n else 0)
' || FLAGGED=1
else echo "  python3 not found: heuristic scan skipped"; fi

echo; echo "== 6. Optional: existing scanners over the same paths =="
ROOT_PATHS=".claude .cursor .codex .agents .gemini .mcp.json .vscode/mcp.json .vscode/settings.json .github/copilot .github/copilot-instructions.md .github/mcp.json CLAUDE.md CLAUDE.local.md AGENTS.md GEMINI.md"
if command -v gitleaks >/dev/null 2>&1; then
  cat > "$TMP/gitleaks-agent.toml" <<'TOML'
[extend]
useDefault = true

[[rules]]
id = "agent-config-inline-credential"
description = "Credential-looking argument saved inside an agent allow list, approval rule or MCP config"
regex = '''(?i)(?:\s-p|sshpass\s+-p\s*|--?(?:password|passwd|pass|pwd|token|secret|api-?key)[ =]|authorization:\s*(?:bearer|basic|token)\s+|://[^/\s:@"]+:)([^\s"'\\)$@{}]{6,})'''
path = '''(?i)(?:^|/)(?:\.claude|\.cursor|\.codex|\.gemini|\.agents|\.vscode|\.github/copilot)/|(?:^|/)\.mcp\.json$|(?:^|/)\.github/mcp\.json$'''
secretGroup = 1
entropy = 3.0
TOML
  # shellcheck disable=SC2086
  gitleaks git . --no-banner --redact --config "$TMP/gitleaks-agent.toml" \
    --log-opts="--all -- $ROOT_PATHS" -f json -r "$TMP/gl.json" >/dev/null 2>&1
  python3 -I - "$TMP/gl.json" <<'PY' || FLAGGED=1
import json, sys
try: d = json.load(open(sys.argv[1]))
except Exception: d = []
for f in d: print(f"  gitleaks {f['RuleID']:32} {f['Commit'][:7]} {f['File']}:{f['StartLine']}")
print("  gitleaks: no findings" if not d else f"  gitleaks: {len(d)} finding(s)")
sys.exit(1 if d else 0)
PY
else echo "  gitleaks not installed (skipped)"; fi
if command -v trufflehog >/dev/null 2>&1; then
  # --no-verification: do not send candidate secrets to third-party APIs from a read-only check
  trufflehog git "file://$PWD" --no-verification --no-update --json 2>/dev/null > "$TMP/th.json"
  python3 -I - "$TMP/th.json" "$ROOT_PATHS" <<'PY' || FLAGGED=1
import json, sys
roots = tuple(sys.argv[2].split()); n = 0
for line in open(sys.argv[1]):
    try: d = json.loads(line)
    except Exception: continue
    g = d.get("SourceMetadata", {}).get("Data", {}).get("Git", {})
    p = g.get("file", "")
    if not any(p == r or p.startswith(r + "/") for r in roots): continue
    n += 1; print(f"  trufflehog {d.get('DetectorName',''):24} {g.get('commit','')[:7]} {p}:{g.get('line','')}")
print("  trufflehog: no findings in agent paths" if not n else f"  trufflehog: {n} finding(s)")
sys.exit(1 if n else 0)
PY
else echo "  trufflehog not installed (skipped)"; fi

echo
if [ "$FLAGGED" -ne 0 ]; then
  echo "RESULT: flagged items above. Rotate any real credential first; removing it from history alone is not enough."
  exit 1
fi
echo "RESULT: nothing flagged (heuristics can miss things)."
exit 0
