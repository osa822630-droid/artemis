# ARTEMIS for Claude

A skills-only plugin for Android test planning, evidence analysis, and optional
ARTEMIS MCP-driven device workflows. No Claude Code commands are required when
installing through Claude Web's **Add marketplace** UI.

## Install from the web

In **Add marketplace**, enter `https://github.com/osa822630-droid/artemis`
(or `osa822630-droid/artemis` if the field requests `owner/repo`). Open
**artemis-marketplace**, install **artemis**, and enable it for your conversation.
UI availability and connector permissions are controlled by Claude, not this
repository; the plugin itself has no paid-plan check.

Try: “Use ARTEMIS to create an Android login test plan. Mark tests not actually
executed as not run.”

See the [Arabic web setup guide](../../docs/claude-web-marketplace.md) for details
and troubleshooting.

## Included skill

- **artemis-mobile-testing** — plans tests, analyzes uploaded evidence, and uses
  connected `mobile_*` tools when available. Its connected-workflow reference
  ships inside the plugin, so installation does not require the Python repo.

## Device access is separate

Installing this plugin does **not** connect a phone, install ADB/Python, or host
ARTEMIS. Without MCP tools it works in planning/evidence mode. Actual device
control requires a separately configured ARTEMIS host and MCP connection.

Claude Web cannot launch the host's stdio process or reach that computer through
`localhost`. Remote access needs a Claude-compatible, authenticated HTTPS MCP
endpoint. This plugin does not provide that gateway or a hosted endpoint and
intentionally ships no `.mcp.json`, local shell commands, or install hooks.
Do not expose an unprotected MCP server, ADB, or admin console to the internet.

## Maintainers

The marketplace index is at the repository root. This directory is the complete
plugin payload: `.claude-plugin/plugin.json` and `skills/`. Keep skill resources
inside the payload, and update both manifest versions together when releasing.

The format follows Anthropic's
[knowledge-work plugin examples](https://github.com/anthropics/knowledge-work-plugins)
and [Agent Skills examples](https://github.com/anthropics/skills).
