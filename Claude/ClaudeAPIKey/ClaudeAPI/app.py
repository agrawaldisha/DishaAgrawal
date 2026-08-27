"""
BrewCo Financial Copilot
--------------------------------
A demo Streamlit app for a fictional US coffee shop chain ("BrewCo") that shows
how to wire Claude (via Google Vertex AI) into a small finance application.

Features:
  1. Dashboard - revenue / expense / profit visuals across stores
  2. AI Financial Analyst - chat with Claude about the numbers
  3. AI Executive Summary - one-click natural language report generation

Run with:
    streamlit run app.py
"""

import os
import json
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from anthropic import AnthropicVertex

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


@st.cache_resource(show_spinner=False)
def get_claude_client() -> AnthropicVertex:
    """Create (and cache) the AnthropicVertex client for the app session."""
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


def generate_report(client: AnthropicVertex, data_summary: dict) -> str:
    """Ask Claude for a one-page executive summary of BrewCo's finances."""
    prompt = (
        "Write a one-page executive summary for BrewCo's owner based on this "
        "financial data (JSON below). Structure it with: Headline takeaway, "
        "Store performance highlights, Cost concerns, and 3 recommended actions. "
        "Keep it under 300 words.\n\n"
        f"{json.dumps(data_summary, indent=2)}"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=900,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ---------------------------------------------------------------------------
# Synthetic BrewCo data
# ---------------------------------------------------------------------------
STORES = ["Downtown", "Uptown", "Airport", "Mall Kiosk", "University"]
EXPENSE_CATEGORIES = ["Rent", "Wages", "Coffee Beans & Supplies", "Utilities", "Marketing", "Equipment"]

BASE_REVENUE = {"Downtown": 42000, "Uptown": 31000, "Airport": 55000, "Mall Kiosk": 18000, "University": 26000}
BASE_EXPENSE_SHARE = {
    "Rent": 0.18, "Wages": 0.35, "Coffee Beans & Supplies": 0.22,
    "Utilities": 0.06, "Marketing": 0.05, "Equipment": 0.05,
}


@st.cache_data(show_spinner=False)
def generate_sample_data(months: int = 6, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    today = date.today().replace(day=1)
    rows = []
    for m in range(months, 0, -1):
        month_date = today - timedelta(days=30 * m)
        month_label = month_date.strftime("%Y-%m")
        for store in STORES:
            seasonal = 1 + 0.08 * np.sin(m)  # mild seasonality
            growth = 1 + (months - m) * 0.01  # slight upward trend over time
            noise = rng.normal(1.0, 0.06)
            revenue = round(BASE_REVENUE[store] * seasonal * growth * noise, 2)

            # Airport had a cost spike two months ago to make the demo interesting
            spike = 1.35 if (store == "Airport" and m == 2) else 1.0

            for cat, share in BASE_EXPENSE_SHARE.items():
                cat_noise = rng.normal(1.0, 0.07)
                cat_spike = spike if cat == "Coffee Beans & Supplies" else 1.0
                expense = round(revenue * share * cat_noise * cat_spike, 2)
                rows.append({
                    "month": month_label,
                    "store": store,
                    "category": cat,
                    "revenue": revenue,
                    "expense": expense,
                })
    return pd.DataFrame(rows)


def build_data_summary(df: pd.DataFrame) -> dict:
    """Compress the raw dataframe into a compact JSON-able summary for Claude."""
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

    expense_by_category = (
        df.groupby("category", as_index=False)["expense"].sum().round(2)
    )

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
# Streamlit UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="BrewCo Financial Copilot", page_icon="☕", layout="wide")

st.title("☕ BrewCo Financial Copilot")
st.caption(
    f"Demo: a small finance app powered by Claude (`{MODEL}`) on Vertex AI · "
    f"project `{PROJECT_ID}` · region `{REGION}`"
)

df = generate_sample_data()

data_summary = build_data_summary(df)

with st.sidebar:
    st.header("Filters")
    selected_stores = st.multiselect("Stores", STORES, default=STORES)
    st.divider()
    st.subheader("Vertex AI connection")
    st.code(f"project_id = {PROJECT_ID}\nregion = {REGION}\nmodel = {MODEL}", language="text")
    st.caption(
        "Auth uses Application Default Credentials. Run "
        "`gcloud auth application-default login` locally, or rely on the "
        "service account when deployed on Google Cloud."
    )

filtered = df[df["store"].isin(selected_stores)]

tab_dashboard, tab_chat, tab_report = st.tabs(
    ["📊 Dashboard", "💬 AI Financial Analyst", "📄 AI Executive Summary"]
)

# --- Dashboard ---------------------------------------------------------
with tab_dashboard:
    monthly = (
        filtered.groupby(["month", "store"], as_index=False)
        .agg(revenue=("revenue", "first"), expense=("expense", "sum"))
    )
    monthly["profit"] = monthly["revenue"] - monthly["expense"]

    total_revenue = monthly["revenue"].sum()
    total_expense = monthly["expense"].sum()
    total_profit = total_revenue - total_expense
    margin = (total_profit / total_revenue * 100) if total_revenue else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:,.0f}")
    c2.metric("Total Expenses", f"${total_expense:,.0f}")
    c3.metric("Net Profit", f"${total_profit:,.0f}")
    c4.metric("Profit Margin", f"{margin:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        fig_rev = px.line(
            monthly, x="month", y="revenue", color="store", markers=True,
            title="Monthly Revenue by Store",
        )
        st.plotly_chart(fig_rev, use_container_width=True)
    with col2:
        fig_profit = px.bar(
            monthly, x="month", y="profit", color="store", barmode="group",
            title="Monthly Profit by Store",
        )
        st.plotly_chart(fig_profit, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        exp_cat = filtered.groupby("category", as_index=False)["expense"].sum()
        fig_pie = px.pie(exp_cat, names="category", values="expense", title="Expense Breakdown by Category")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col4:
        store_totals = monthly.groupby("store", as_index=False)[["revenue", "expense"]].sum()
        fig_store = px.bar(
            store_totals, x="store", y=["revenue", "expense"], barmode="group",
            title="Revenue vs Expense by Store (All Time)",
        )
        st.plotly_chart(fig_store, use_container_width=True)

# --- AI Financial Analyst (chat) ---------------------------------------
with tab_chat:
    st.write(
        "Ask Bean Counter anything about BrewCo's numbers — e.g. "
        "*\"Which store has the best margin?\"* or *\"Why did costs spike at the Airport store?\"*"
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # list of {"role", "content"} for Claude
        st.session_state.chat_display = []  # list of (role, text) for rendering

    for role, text in st.session_state.chat_display:
        with st.chat_message(role):
            st.markdown(text)

    question = st.chat_input("Ask about BrewCo's finances...")
    if question:
        st.session_state.chat_display.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Bean Counter is crunching the numbers..."):
                try:
                    client = get_claude_client()
                    answer = ask_claude(
                        client, data_summary, question, st.session_state.chat_history
                    )
                except Exception as e:
                    answer = (
                        "⚠️ Couldn't reach Claude on Vertex AI. Make sure you've run "
                        "`gcloud auth application-default login`, that the Vertex AI API "
                        "is enabled, and that your project has access to Claude models.\n\n"
                        f"Error: `{e}`"
                    )
                st.markdown(answer)

        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.session_state.chat_display.append(("assistant", answer))

    if st.session_state.chat_display:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.session_state.chat_display = []
            st.rerun()

# --- AI Executive Summary ----------------------------------------------
with tab_report:
    st.write("Generate a one-page, owner-friendly financial summary written by Claude.")
    if st.button("Generate Executive Summary", type="primary"):
        with st.spinner("Writing the report..."):
            try:
                client = get_claude_client()
                report = generate_report(client, data_summary)
                st.markdown(report)
                st.download_button(
                    "Download report (.md)", report, file_name="brewco_executive_summary.md"
                )
            except Exception as e:
                st.error(
                    "Couldn't reach Claude on Vertex AI. Check gcloud auth, the Vertex AI "
                    f"API being enabled, and model access.\n\nError: `{e}`"
                )

with st.expander("See the raw sample data"):
    st.dataframe(filtered, use_container_width=True)
