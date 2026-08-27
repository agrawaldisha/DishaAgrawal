# Instructions: Build the TaskFlow MCP Server

Paste this whole file into Claude Code (or say "follow BUILD_TASKFLOW_MCP_SERVER.md")
and it will scaffold, write, and connect the exact server described below —
no manual copy-pasting of code required.

---

## Goal

Create a working local MCP server called **TaskFlow** that demonstrates all
four MCP primitives (Tools, Resources, Prompts, Sampling), using Python +
FastMCP, and connect it to Claude Code.

## Step 1 — Prerequisites check

Run and confirm each of these works before continuing:
```
python --version        # need 3.11 or 3.12
uv --version             # if missing, install:
                          #   macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
                          #   Windows:     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
claude --version         # Claude Code CLI
```

## Step 2 — Project scaffold

Create this exact structure in a new folder named `taskflow-mcp-server`:
```
taskflow-mcp-server/
├── server.py
├── data/
│   ├── tasks.json
│   └── config.json
├── .env
├── .gitignore
└── pyproject.toml
```

Commands:
```
mkdir taskflow-mcp-server
cd taskflow-mcp-server
uv init
uv venv
uv add mcp
mkdir data
echo ".env" >> .gitignore
```

`.env` contents:
```
APP_NAME=TaskFlow
APP_VERSION=1.0.0
DATABASE_URL=sqlite:///taskflow.db
API_SECRET=your-secret-key-here
```

## Step 3 — Write server.py

Write a single file `server.py` implementing ALL of the following, in this
order. Use `FastMCP` from `mcp.server.fastmcp`.

### 3a. Bootstrap
- Import `FastMCP`, `Context` from `mcp.server.fastmcp`; `ServerSession` from
  `mcp.server.session`; `SamplingMessage`, `TextContent` from `mcp.types`;
  plus `json`, `os`, `datetime`.
- Initialize `mcp = FastMCP(name="TaskFlow MCP Server", instructions=...)`
  with instructions describing that this connects to a task management app
  exposing Tools, Resources, Prompts, and Sampling.
- Define an in-memory `TASKS_DB` dict seeded with 3 sample tasks (T001 "Fix
  login bug"/open/high/alice, T002 "Write API docs"/in_progress/medium/bob,
  T003 "Deploy to staging"/done/high/alice).
- Define a `CONFIG` dict with `app_name`, `version`, `max_tasks_per_user: 50`,
  and `allowed_statuses: ["open", "in_progress", "review", "done"]`.

### 3b. Tools (`@mcp.tool()`) — 5 total
1. `get_task(task_id: str) -> dict` — fetch one task, return error dict if missing.
2. `list_tasks(status=None, assignee=None, priority=None) -> list` — filter tasks.
3. `create_task(title: str, priority="medium", assignee=None) -> dict` —
   auto-generate next `T00N` id, set status "open", add `created` timestamp.
4. `update_task_status(task_id: str, new_status: str) -> dict` — validate
   against `CONFIG["allowed_statuses"]`, return error if invalid or not found.
5. `delete_task(task_id: str) -> dict` — remove and return the deleted task.

Give every tool a clear docstring (used as the LLM-facing description) and
type-annotated parameters.

### 3c. Resources (`@mcp.resource()`) — 5 total
1. `taskflow://config` → JSON dump of `CONFIG`.
2. `taskflow://tasks/all` → JSON dump of all tasks.
3. `taskflow://tasks/{task_id}` → JSON of one task (templated URI).
4. `taskflow://stats` → computed counts by status / priority / assignee.
5. `taskflow://schema` → JSON description of the task data model's fields.

### 3d. Prompts (`@mcp.prompt()`) — 3 total
1. `daily_standup(assignee: str) -> str` — builds a YESTERDAY/TODAY/BLOCKERS
   prompt from that user's tasks split into in_progress/open/done.
2. `triage_high_priority() -> str` — prompt asking Claude to rank all open
   high-priority tasks, flag risks, suggest owners, recommend next actions.
3. `write_task_description(feature_name: str, context: str = "") -> str` —
   prompt asking Claude to write a structured TITLE/DESCRIPTION/ACCEPTANCE
   CRITERIA/DEFINITION OF DONE/EFFORT/PRIORITY task entry.

### 3e. Sampling — 1 tool
`async def ai_task_summary(assignee: str, ctx: Context[ServerSession, None]) -> str`
- Collect that user's tasks deterministically first.
- If none found, return early with a plain message.
- Otherwise build a prompt asking for: a one-paragraph workload summary, the
  most pressing item, and any risk/bottleneck — under 150 words.
- Call `await ctx.session.create_message(messages=[SamplingMessage(role="user",
  content=TextContent(type="text", text=prompt))], max_tokens=300)`.
- Return the text content prefixed with `"AI Summary for {assignee}:\n\n"`.

### 3f. Entry point
```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Step 4 — Sanity-test the server

```
uv run server.py        # should start with no errors, Ctrl+C to stop
npx @modelcontextprotocol/inspector uv run server.py
```
In the Inspector UI (http://localhost:5173): list tools, call `list_tasks`,
read the `taskflow://stats` resource, and trigger the `daily_standup` prompt
to confirm all four primitives respond correctly.

## Step 5 — Connect to Claude Code

From inside `taskflow-mcp-server/`:
```
claude mcp add taskflow -- uv run server.py
claude mcp list
```
Then start `claude` and test:
```
"Show me all high-priority tasks"
"Create a task titled 'Optimize database queries'"
"Give me an AI summary of Alice's tasks"
```

Alternative (shareable project-scope config) — create `.mcp.json` in the
project root instead:
```json
{
  "mcpServers": {
    "taskflow": {
      "command": "uv",
      "args": ["run", "server.py"]
    }
  }
}
```

## Step 6 — Production notes (optional, do not do by default)
- Swap transport to `mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)`
  only if deploying remotely.
- Never hardcode secrets — pass `DATABASE_URL` / `API_SECRET` via the `env`
  block in the MCP config, not inline in `server.py`.
- Keep only actively-used MCP servers registered; each one adds its tool
  schemas to every conversation's context window.

## Troubleshooting reference
- **Shows "disconnected" in `claude mcp list`** → run `uv run server.py`
  directly and read stderr; usually wrong Python version or import error.
- **Tools work but Resources/Prompts don't appear** → confirm the
  `@mcp.resource()` / `@mcp.prompt()` decorators are present and the file is
  saved; restart the client.
- **Sampling errors** → the host must have sampling enabled; check client
  settings.
- **JSON config silently breaks everything** → validate `.mcp.json` /
  `claude_desktop_config.json` at jsonlint.com — one missing comma disables
  all servers.
- **"uv: command not found"** → use the full absolute path to `uv` (find it
  with `which uv`) in the `command` field of the config.
