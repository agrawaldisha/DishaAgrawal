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

## Troubleshooting

- **"Couldn't reach Claude on Vertex AI"** in the app → almost always an auth
  or API-enablement issue. Re-run `gcloud auth application-default login`
  and confirm `aiplatform.googleapis.com` is enabled for the project.
- **403 / model not found** → the model may not be enabled in the region
  you're using. Try `global` or check Model Garden for your enabled regions.
- **Slow first response** → normal cold-start for the client; subsequent
  calls in the same session are faster.
