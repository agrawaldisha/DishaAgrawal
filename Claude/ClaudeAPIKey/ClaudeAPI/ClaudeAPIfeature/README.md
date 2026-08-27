# ☕ BrewCo Financial Copilot

A small demo finance app for a fictional US coffee shop chain, "BrewCo,"
built to show how to wire **Claude on Google Vertex AI** into a real app.

It has three parts:
1. **Dashboard** — revenue / expense / profit charts across 5 store locations
2. **AI Financial Analyst** — a chat panel where Claude answers questions about the numbers
3. **AI Executive Summary** — one click generates an owner-friendly written report

The data is synthetic (generated in-app), including a deliberate cost spike at
the Airport location so the AI analyst has something interesting to notice.

## 1. One-time GCP setup

You said your project `learning-development-c-000027` already has access to
Claude Haiku models, so most of this is likely already done. For reference:

```bash
# Set your project
gcloud config set project learning-development-c-000027

# Make sure the Vertex AI API is enabled
gcloud services enable aiplatform.googleapis.com

# Authenticate so the Anthropic SDK can find Application Default Credentials
gcloud auth application-default login
```

In Vertex AI **Model Garden**, search "Claude" and confirm Claude Haiku 4.5
shows as enabled for your project/region (Anthropic models on Vertex are
region-specific — `us-east5` is a safe default; `global` also works for many
models).

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure (optional — defaults already match your project)

The app reads these environment variables, with sensible defaults baked in:

| Variable | Default |
|---|---|
| `GCP_PROJECT_ID` | `learning-development-c-000027` |
| `CLAUDE_VERTEX_REGION` | `us-east5` |
| `CLAUDE_MODEL` | `claude-haiku-4-5@20251001` |

Override if needed, e.g.:
```bash
export CLAUDE_VERTEX_REGION=global
```

## 4. Run it

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## How the Claude call works

The core of the integration is just a few lines (see `app.py`):

```python
from anthropic import AnthropicVertex

client = AnthropicVertex(project_id="learning-development-c-000027", region="us-east5")

response = client.messages.create(
    model="claude-haiku-4-5@20251001",
    max_tokens=800,
    system="You are Bean Counter, BrewCo's financial analyst...",
    messages=[{"role": "user", "content": "Which store has the best margin?"}],
)
print(response.content[0].text)
```

The app compresses the pandas dataframe into a compact JSON summary
(store totals, monthly figures, expense-by-category) before sending it to
Claude, rather than sending the raw table — this keeps costs and latency
low and mirrors how you'd handle a larger real dataset.

## Progressive demo scripts

Alongside the Streamlit app, this folder has 5 standalone scripts that build
up Claude API concepts one at a time — good for walking through live in a
demo, each one runnable on its own:

| Script | Concept | What it shows |
|---|---|---|
| `feature1_basic.py` | Basic message | One question in, one answer out — no history, no system prompt |
| `feature2_multiturn.py` | Multi-turn conversation | Keeping a growing `history` list so Claude has context across turns |
| `feature3_system_prompt.py` | System prompts | Giving Claude a persistent persona/rules, with a side-by-side comparison against no system prompt |
| `feature4_streaming.py` | Streaming | Printing the reply token-by-token as it arrives, instead of waiting for the full response |
| `feature5_tools.py` | Tool use (function calling) | Claude calling a real Python function (`get_store_financials`) to ground its answer in actual data instead of guessing |

Run any of them directly:

```bash
python feature1_basic.py
python feature2_multiturn.py
python feature3_system_prompt.py
python feature4_streaming.py
python feature5_tools.py
```

They all use the same `learning-development-c-000027` / `us-east5` /
`claude-haiku-4-5@20251001` config as `app.py` and `ask_claude.py` — the
`get_store_financials` fake dataset in `feature5_tools.py` mirrors the same
5 BrewCo stores used in the dashboard.

## Troubleshooting

- **"Couldn't reach Claude on Vertex AI"** in the app → almost always an auth
  or API-enablement issue. Re-run `gcloud auth application-default login`
  and confirm `aiplatform.googleapis.com` is enabled for the project.
- **403 / model not found** → the model may not be enabled in the region
  you're using. Try `global` or check Model Garden for your enabled regions.
- **Slow first response** → normal cold-start for the client; subsequent
  calls in the same session are faster.
