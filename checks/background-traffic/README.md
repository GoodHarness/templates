# Check your own background traffic

Claude Code's background agents send requests you never typed. While an agent works, Claude Code sends its transcript to the model on a timer to write the status line. This check shows those requests on your own machine.

Why this matters, what we saw, and a dated verdict: [What your agent sends when you're not watching](%%NEWSLETTER_URL%%).

## What you need

- Claude Code 2.1.274 or later (needed for `OTEL_LOG_RAW_API_BODIES=file:`; [monitoring docs](https://code.claude.com/docs/en/monitoring-usage)). The debug lines below match 2.1.318.
- A throwaway folder with no secrets. Request bodies hold your entire conversation, tool output included.

## Run it

1. In the throwaway folder, paste the four `export` lines of [`check.sh`](check.sh) into your shell. Don't execute the file: the exports have to stay in your shell.
2. Start Claude Code with the debug file: `claude --debug-file ./claude-debug.txt`.
3. In that session, ask for one or two background sub-agents that make several short tool calls.
4. When they finish, exit Claude Code and run the three `grep` lines.

## Read the result

| Line | What it means |
| --- | --- |
| `Forking for summary` | A status request was sent for a background agent |
| `Skipping summary` | A tick was skipped because the agent's transcript hadn't changed |
| Files matching `most recent action` | The status requests' full bodies. Open one to see the model, the transcript and the tool list it carried |

`/usage` shows how much went to sub-agents overall; it doesn't split out the status requests.

## Limits

- The debug lines are internal and may change in any release. Re-check after updates.
- OpenTelemetry's per-request events often miss side requests ([#98193](https://github.com/anthropics/claude-code/issues/98193)), so count from the debug log.
- Dollar figures Claude Code shows are estimates, not your bill ([costs docs](https://code.claude.com/docs/en/costs)).
- Delete `otel-bodies/` and `claude-debug.txt` when you're done.

## Our notes

What we saw in two runs on 2.1.318, with redacted log excerpts: [try-notes.md](try-notes.md). Tried by hand; no numbers.
