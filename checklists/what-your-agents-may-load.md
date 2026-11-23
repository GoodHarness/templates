# What your agents may load

A checklist for teams that let coding agents start MCP servers and editor extensions.
It's Recommended practice from the Good Harness field notes of 23 Nov 2026 (https://buttondown.com/goodharness/archive/tools-changed-after-approval/).
Good Harness hasn't measured it. Every value below is a dummy.

- [ ] List every MCP server and extension your agents load, from `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`, `.codex/config.toml` and `~/.copilot/mcp-config.json`.
- [ ] Replace `@latest`, untagged images and bare package names with exact versions or image digests.
- [ ] For Python servers, install from a hash-checked lock file and launch the installed server directly, not through `uvx`.
- [ ] At org level, allow servers by exact command or URL, never by name alone.
- [ ] Lock the allowlist in managed settings, so users can't widen it.
- [ ] Pin extensions to exact versions. Use an update delay or install cooldown where your editor has one.
- [ ] Give each MCP server the narrowest credentials it needs.
- [ ] Name an owner who re-reviews the pinned versions on a schedule.

An exact version pins the top package only: `uvx` and `npx` can still re-resolve its dependencies.

## Claude Code: managed settings

```json
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverCommand": ["npx", "-y", "@example/mcp-server@1.4.2"] },
    { "serverUrl": "https://mcp.example.com/*" }
  ]
}
```

Source: https://code.claude.com/docs/en/managed-mcp

## Codex: requirements.toml

Use the table form; the plain string form ignores arguments.

```toml
[mcp_servers.example-server.identity]
command = { executable = "npx", args = [
  { match = "exact", value = "-y" },
  { match = "exact", value = "@example/mcp-server@1.4.2" },
] }
```

Source: https://learn.chatgpt.com/docs/enterprise/managed-configuration

## Cursor: Enterprise dashboard

MCP Allowlist entries (no wildcard after the version):

```text
Command entry: *npx -y @example/mcp-server@1.4.2
URL entry:     https://mcp.example.com/*
```

Allowed extensions (client 2.1+):

```json
{ "example-publisher.example-ext": ["1.4.2"], "other-publisher": "stable" }
```

Sources: https://cursor.com/docs/enterprise/model-and-integration-management, https://cursor.com/docs/enterprise/identity-and-access-management

## Copilot: enterprise managed-settings.json

```json
{
  "allowedMcpServers": [
    { "serverCommand": ["npx", "-y", "@example/mcp-server@1.4.2"] },
    { "serverUrl": "https://mcp.example.com/*" }
  ],
  "deniedMcpServers": [ { "serverUrl": "https://*.untrusted.example.com/*" } ]
}
```

The built-in GitHub MCP server can't be blocked here. For VS Code extensions, use `extensions.allowed` with exact versions.

Sources: https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings, https://code.visualstudio.com/docs/enterprise/extensions
