#!/usr/bin/env python3
"""
BrewCo Financial Copilot - CLI version (no Streamlit, no browser)
--------------------------------------------------------------
Same logic as app.py's "AI Financial Analyst" tab, but runs as a plain
terminal chat. Type a question, get an answer, repeat. Type 'exit' to quit.

Run:
    python demo_cli.py
"""

import os
import json
from datetime import date, timedelta

import numpy as np #generate random data
import pandas as pd #create datafrmaes 
from anthropic import AnthropicVertex # Model LLM 

# ---------------------------------------------------------------------------
# Vertex AI / Claude configuration
# ---------------------------------------------------------------------------
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "learning-development-c-000027")
REGION = os.environ.get("CLAUDE_VERTEX_REGION", "us-east5")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5@20251001")

SYSTEM_PROMPT = """You are "Bean Counter", the AI financial analyst for BrewCo,
a US coffee shop chain with several store locations. You are given a JSON
summary of BrewCo's sales and expense data. Answer questions clearly and
concisely for a small-business owner audience (not accountants). Use dollar
figures, percentages, and short bullet points where helpful. If the data
doesn't contain what's needed to answer, say so plainly instead of guessing.
Never invent numbers that are not in the provided data."""


def get_claude_client() -> AnthropicVertex:
    """Create the AnthropicVertex client. Built once, at the top of main()."""
    return AnthropicVertex(project_id=PROJECT_ID, region=REGION)


def ask_claude(client: AnthropicVertex, data_summary: dict, question: str,
               history: list[dict]) -> str:
    """Send a question + data context + prior turns to Claude and return the reply."""
    context_msg = (
        "Here is the current BrewCo financial data summary (JSON):\n"
        f"{json.dumps(data_summary, indent=2)}\n\n"
        f"Owner's question: {question}"
    )
    messages = history + [{"role": "user", "content": context_msg}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


# ---------------------------------------------------------------------------
# Synthetic BrewCo data (same as app.py, minus the @st.cache_data decorator —
# a plain Python script doesn't need caching, since the script only runs once
# top to bottom, not on every keystroke like Streamlit does)
# ---------------------------------------------------------------------------
STORES = ["Downtown", "Uptown", "Airport", "Mall Kiosk", "University"]
BASE_REVENUE = {"Downtown": 42000, "Uptown": 31000, "Airport": 55000, "Mall Kiosk": 18000, "University": 26000}
BASE_EXPENSE_SHARE = {
    "Rent": 0.18, "Wages": 0.35, "Coffee Beans & Supplies": 0.22,
    "Utilities": 0.06, "Marketing": 0.05, "Equipment": 0.05,
}


def generate_sample_data(months: int = 6, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    today = date.today().replace(day=1)
    rows = []
    for m in range(months, 0, -1):
        month_date = today - timedelta(days=30 * m)
        month_label = month_date.strftime("%Y-%m")
        for store in STORES:
            seasonal = 1 + 0.08 * np.sin(m)
            growth = 1 + (months - m) * 0.01
            noise = rng.normal(1.0, 0.06)
            revenue = round(BASE_REVENUE[store] * seasonal * growth * noise, 2)
            spike = 1.35 if (store == "Airport" and m == 2) else 1.0
            for cat, share in BASE_EXPENSE_SHARE.items():
                cat_noise = rng.normal(1.0, 0.07)
                cat_spike = spike if cat == "Coffee Beans & Supplies" else 1.0
                expense = round(revenue * share * cat_noise * cat_spike, 2)
                rows.append({
                    "month": month_label, "store": store, "category": cat,
                    "revenue": revenue, "expense": expense,
                })
    df = pd.DataFrame(rows)          # <- build the DataFrame first
    df.to_csv("random_data.csv", index=False)   # <- then save it, once
    return df
    


def build_data_summary(df: pd.DataFrame) -> dict:
    monthly = (
        df.groupby(["month", "store"], as_index=False)
        .agg(revenue=("revenue", "first"), expense=("expense", "sum"))
    )
    monthly["profit"] = monthly["revenue"] - monthly["expense"]

    store_totals = (
        monthly.groupby("store", as_index=False)
        .agg(total_revenue=("revenue", "sum"), total_expense=("expense", "sum"), total_profit=("profit", "sum"))
        .round(2)
    )
    expense_by_category = df.groupby("category", as_index=False)["expense"].sum().round(2)
    latest_month = df["month"].max()
    latest = monthly[monthly["month"] == latest_month].round(2)

    return {
        "months_covered": sorted(df["month"].unique().tolist()),
        "stores": STORES,
        "store_totals_all_time": store_totals.to_dict(orient="records"),
        "expense_by_category_all_time": expense_by_category.to_dict(orient="records"),
        "latest_month": latest_month,
        "latest_month_by_store": latest.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# CLI chat loop (this replaces st.chat_input / st.session_state / st.markdown)
# ---------------------------------------------------------------------------
def main():
    print(f"Connecting to Claude ({MODEL}) on Vertex AI — project '{PROJECT_ID}', region '{REGION}'")
    client = get_claude_client()

    # Build the data once, up front — equivalent to the two lines that ran
    # at the top of app.py's UI section.
    df = generate_sample_data()
    data_summary = build_data_summary(df)

    # A plain Python list stands in for st.session_state.chat_history —
    # in Streamlit this had to survive reruns; here the script just keeps
    # running in one process, so a normal variable is enough.
    history = []

    print("\nBrewCo Financial Copilot (CLI) — ask Bean Counter about the numbers.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        try:
            answer = ask_claude(client, data_summary, question, history)
        except Exception as e:
            print(f"\n⚠️  Couldn't reach Claude on Vertex AI: {e}\n")
            continue

        # Same two history.append() lines as app.py's chat tab
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        print(f"\nBean Counter: {answer}\n")


if __name__ == "__main__":
    main()