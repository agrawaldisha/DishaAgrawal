# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

This is **not a software project** — there is no source code, package manager, build system, linter, or test suite. It is a Claude Code working directory containing personal notes and Claude Code configuration (hooks, a custom skill, MCP server definitions). There are no build/lint/test commands to run here.

Contents:
- `notes.txt` — free-form personal notes (meeting notes, TODOs, reminders).
- `.claude/` — Claude Code configuration for this project (hooks, skills, settings).
- `.mcp.json` — MCP server definitions (`github`, `db`).
- `.env` — local environment variables.

## Custom skill

- `.claude/skills/summarize-txt/SKILL.md` — when asked to "summarize" a `.txt` file, do **not** write a prose summary. Instead compute word-frequency counts (lowercase, split on non-alphanumeric chars, keep stopwords, sort by count desc then alphabetically) and output as a markdown table with total/distinct word counts appended.

## Hooks (`.claude/settings.json`)

Three hooks are wired up and active for this project:
- **PreToolUse** (`Edit|Write`) → `.claude/hooks/block_sensitive_files.sh`: blocks any edit/write to paths containing `.env` or `/secrets/`, exiting with code 2 to reject the tool call.
- **PostToolUse** (`Edit|Write`) → `.claude/hooks/log_edits.sh`: appends every edited/written file path with a timestamp to `.claude/edit_log.txt`.
- **Stop** → `.claude/hooks/session_summary.sh`: on turn end, appends a summary line (edit count so far) to `.claude/hooks/session_summary.log`.

Because of the PreToolUse hook, direct edits to `.env` or anything under a `secrets/` folder will be rejected — this is enforced by policy, not just convention.

## MCP servers (`.mcp.json`)

- `github` — HTTP MCP server at `api.githubcopilot.com/mcp` (uses a bearer token defined inline in `.mcp.json`).
- `db` — stdio MCP server via `@bytebase/dbhub`, connected to a local Postgres instance (`postgresql://postgres:root@localhost:5432/postgres`).

Both are enabled via `.claude/settings.local.json` (`enabledMcpjsonServers`).

**Security note:** `.mcp.json` currently stores the GitHub PAT inline rather than via an environment variable reference. Treat this file as sensitive, and prefer referencing secrets from `.env` (which the hook above protects from edits) rather than hardcoding them here.
