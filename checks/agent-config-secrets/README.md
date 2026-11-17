# Check your agent config for secrets

Coding agents save what you approve. Claude Code writes "Yes, and don't ask again" approvals to `.claude/settings.local.json`, inside your repo, where a command could be saved word for word. Since 2.1.323, Claude Code skips rules that look like secrets, but files saved earlier keep theirs. Other agents keep similar files in the repo or your home folder. This check looks for those files in your repo and its history, and flags secrets inside them.

Why this matters, where each agent keeps its approvals, and two real repos: [Keep secrets out of your agent's config files](https://buttondown.com/goodharness/archive/keep-secrets-out-of-your-agents-config-files/).

## What it does

`check.sh` is read-only. It never changes your repo, index, refs or config. It:

1. lists agent config files tracked now (`.claude/`, `.cursor/`, `.codex/`, `.agents/`, `.gemini/`, `.github/copilot/`, `.mcp.json`, `.vscode/mcp.json` and the instruction files);
2. lists every agent config path that was ever in history, on all branches;
3. flags local-only files that are or were tracked, such as `.claude/settings.local.json`;
4. tells you whether your repo's own `.gitignore` covers those files, or only a global exclude on one machine;
5. scans every added line in those paths for credentials, including passwords inside commands, and prints them redacted;
6. runs gitleaks and TruffleHog over the same paths if you have them installed. TruffleHog runs with `--no-verification`, so no candidate secret is sent anywhere.

## Run it

Only on repositories you own:

```bash
bash check.sh path/to/your/repo
```

It needs `git` and `python3`. Exit code 0 means nothing was flagged, 1 means something was, 2 means the path isn't a git repo.

## If it finds something

1. **Rotate the credential first.** Removing it from the file, or rewriting history, doesn't reach forks, clones or mirrors.
2. Untrack the local file: `git rm --cached .claude/settings.local.json`, then commit.
3. Add the lines in [`gitignore-snippet.txt`](gitignore-snippet.txt) to your `.gitignore`, and the local-file lines to `.npmignore` and `.dockerignore`.
4. Stop typing secrets into commands your agent runs. Reference them as variables (`$DB_URL`) or through a secret manager.

## What we saw by hand

Two tries by hand, on Claude Code 2.1.318 and 2.1.325, with dummy values: what the prompt offered, what the file saved and what kept it out of git. See [TRIED.md](TRIED.md). It's an observation, not a measurement.

## Limits

- The checks are heuristics. They can miss things, and they can flag look-alikes.
- Where Cursor's IDE "Always run" button saves approvals is not documented, so the check can't look there.
- Home-folder files (`~/.codex/`, `~/.copilot/`, `~/.cursor/`) aren't in your repo, so this check doesn't read them. They are still plain text: keep them out of dotfiles repos and backups.
- Vendors change these paths. Checked against the vendors' docs on 10 Nov 2026 and Claude Code's changelog through 2.1.325 (16 Nov 2026).
