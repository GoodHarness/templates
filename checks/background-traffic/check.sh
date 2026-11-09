# Good Harness · check your own background traffic (Claude Code 2.1.318)
# Throwaway folder only: request bodies hold your entire conversation.
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_LOGS_EXPORTER=console
export OTEL_METRICS_EXPORTER=console
export OTEL_LOG_RAW_API_BODIES=file:./otel-bodies
claude --debug-file ./claude-debug.txt
# start a background agent, let it work, exit, then:
grep -c "Forking for summary" claude-debug.txt
grep -c "Skipping summary" claude-debug.txt
grep -rl "most recent action" otel-bodies | wc -l
