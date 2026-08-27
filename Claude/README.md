# Claude

Hands-on study material for building with Claude — from first API call
through to multi-agent orchestration. Previously a standalone repository,
now consolidated here.

## Contents

### `ClaudeBasics/`
Introductory notes on the Claude platform — models, capabilities, and
where each one fits.

### `ClaudeAPIKey/`
Working with the Messages API. Five progressive scripts under
`ClaudeAPI/ClaudeAPIfeature/` cover basic calls, multi-turn conversation,
system prompts, streaming, and tool use, with a Streamlit app
(`ClaudeAPI/app.py`) that exercises them against a sample CSV.

### `ClaudeCode/`
A demo project showing project-level Claude Code configuration — hooks
that block edits to sensitive files, log edits, and summarize a session,
plus a custom `summarize-txt` skill and a `CLAUDE.md`.

### `ClaudeMCPServer/`
Model Context Protocol notes and a step-by-step guide to building the
TaskFlow MCP server from scratch.

### `ClaudeSubagents/`
Subagent design — when to delegate, how to scope a subagent's tools, and
how results flow back — with a config-drift orchestration demo.

### `Claude_Certification_Practice_Assessment.xlsx`
Practice questions for certification prep.

## Notes

No credentials are committed. The API scripts read `ANTHROPIC_API_KEY`
from the environment, and `.env` is ignored.
