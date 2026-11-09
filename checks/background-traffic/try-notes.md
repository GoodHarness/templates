# Try notes: two runs by hand on Claude Code 2.1.318

**Evidence label: Tried.** Two runs, by hand, on 4 and 5 November 2026. Two runs are not a measurement, so these notes carry no counts, sizes, rates or costs. They show what the logs and request bodies looked like, so you know what to look for when you run [`check.sh`](check.sh) yourself.

Why this matters and the dated verdict: [What your agent sends when you're not watching](https://buttondown.com/goodharness/archive/background-agents/).

**Redacted:** the request bodies carry a device id, an account UUID, a session id and the git user name. None of them appear here. Folder paths are left out too.

## Setup (both runs)

- **Claude Code:** 2.1.318, on a Mac, in auto permission mode.
- **Model:** Opus 5.5 (`claude-opus-5-5`) for the session.
- **Project:** a throwaway git repo holding only `notes.txt`. No secrets, no unofficial patch, nothing pushed.
- **Logging:** the four exports in [`check.sh`](check.sh), and Claude Code started with `--debug-file ./claude-debug.txt`. Request bodies were written to `./otel-bodies`.

## Run 1: agents that appeared to wait on one long command

**When:** Wed 4 Nov 2026, 23:19–23:23 Warsaw time.

**Prompt:** start two background agents, each running `sleep 20` eight times, then reading `notes.txt`.

**What the debug log showed** (`grep "AgentSummary" claude-debug.txt`):

- **22:20:50 UTC, first tick.** A timer fired for each agent, and each one logged "Forking for summary". The status lines that came back were "Starting sleep and date loop" and "Starting sleep timer loop".
- **22:21:23 UTC, next tick.** Both timers fired again, and both logged "Skipping summary … transcript unchanged".
- **Every later tick** was skipped the same way, until the agents finished.

**Our reading:** the first status line suggests each agent ran its sleeps as one long loop, so its transcript barely changed while it waited. In this version, a status request seems to need a changed transcript, not just the timer. We can't confirm the long loop from the logs alone.

## Run 2: agents making many short calls

**When:** Thu 5 Nov 2026, 11:52–11:57 Warsaw time, in a fresh folder.

**Prompt:** "Start two background subagents. Each one must run `sleep 15` and then `date` as separate Bash calls, one command per call, 16 times. No loops and no chaining with `&&` or `;`. Then read notes.txt and report the timestamps. Don't change any files."

**What the debug log showed:**

- **No "Skipping summary" lines.** Every tick logged "Forking for summary" for each agent still working.
- **Status lines tracked the work,** from the first "Summary result" at 10:52:24 UTC to the last at 10:57:21 UTC. For example: "Running date after first sleep", "Recording the tenth `date` output", "Printing date after thirteenth sleep".
- **The numbering jumps** (fourth, then sixth, then seventh), because a tick is slower than one sleep-and-date step.

## What one status request contains

We opened two request bodies: the first status request of run 1, sent seconds after the agents started, and a late one from run 2. `grep -rl "most recent action" otel-bodies` finds them.

| Part | What we saw |
| --- | --- |
| Model | `claude-opus-5-5`, the session's own model, in both bodies. Not a small model. |
| Header | `cc_version=2.1.318` and `cc_is_subagent=true` |
| Settings | Adaptive thinking, effort medium |
| Transcript | The agent's whole context so far: its task prompt, the system reminders, and, in the late body, every tool call and every result up to the newest step |
| Tool list | The full tool list again (Agent, Artifact, Bash, Edit, Read, Skill, ToolSearch, Write and more), although the instruction says not to use tools |
| Instruction | Describe the most recent action in a few words, present tense, without tools. Appended to the last user message, after the newest tool result |
| Previous status | The late body adds the last status line: `Previous: "Recording the thirteenth date output" — say something NEW.` |
| Caching | `cache_control: ephemeral` markers on the system prompt and on the agent's second-to-last tool call |
| Personal data | A device id, an account UUID, a session id and the git user name, in `metadata` and the context. Removed here. |

**So:** the late request carried more than the early one, because the transcript it resends grows as the agent works.

**What a request body can't show:** what was actually read from the cache. The prompt is marked for caching, but we make no claim about savings.

## What `/usage` said

`/usage` attributed most of each session to sub-agents and suggested giving general-purpose sub-agents a cheaper model. It doesn't split out the status requests. Its figures are Claude Code's own estimates, not a bill, so we don't publish them.

## Limits

- **Two runs, one version.** The debug lines are internal and may change in any release. Re-check after updates.
- **No numbers.** A measured number needs an eval with run counts. These notes are what we saw, not how often or how much.
- **Raw files not published.** They hold personal data and the whole conversation. If you share yours, redact them first.
