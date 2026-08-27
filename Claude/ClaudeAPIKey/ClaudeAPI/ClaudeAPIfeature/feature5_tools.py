#!/usr/bin/env python3
"""
Feature 5: Tool Use (Function Calling)
Demonstrates giving Claude a "tool" it can call to fetch real data instead
of guessing. Claude decides WHEN to call it; your code actually runs it and
sends the result back for Claude to use in its final answer.

Run:
    python feature5_tools.py
"""

import json
from anthropic import AnthropicVertex

client = AnthropicVertex(
    project_id="learning-development-c-000027",
    region="us-east5",
)

MODEL = "claude-haiku-4-5@20251001"

# --- A fake "database" of store financials, and the function that reads it ---
STORE_DATA = {
    "Downtown":    {"revenue": 42000, "expenses": 31000},
    "Uptown":      {"revenue": 31000, "expenses": 24500},
    "Airport":     {"revenue": 55000, "expenses": 48000},
    "Mall Kiosk":  {"revenue": 18000, "expenses": 15200},
    "University":  {"revenue": 26000, "expenses": 19800},
}


def get_store_financials(store_name: str) -> dict:
    """The actual Python function Claude will trigger."""
    data = STORE_DATA.get(store_name)
    if not data:
        return {"error": f"No data found for store '{store_name}'"}
    profit = data["revenue"] - data["expenses"]
    margin = round(profit / data["revenue"] * 100, 1)
    return {**data, "profit": profit, "margin_pct": margin}


# --- Describe the tool to Claude so it knows it exists and how to call it ---
tools = [
    {
        "name": "get_store_financials",
        "description": "Get revenue, expenses, profit, and margin for one BrewCo store.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_name": {
                    "type": "string",
                    "description": "One of: Downtown, Uptown, Airport, Mall Kiosk, University",
                }
            },
            "required": ["store_name"],
        },
    }
]

messages = [
    {"role": "user", "content": "Which BrewCo store has the best profit margin, "
                                 "and what is it?"}
]

# --- Step 1: ask Claude; it may respond with a tool call instead of an answer ---
response = client.messages.create(
    model=MODEL,
    max_tokens=500,
    tools=tools,
    messages=messages,
)

# Claude might need to call the tool multiple times (once per store here)
while response.stop_reason == "tool_use":
    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"[Claude is calling get_store_financials(store_name={block.input['store_name']!r})]")
            result = get_store_financials(**block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })

    messages.append({"role": "user", "content": tool_results})

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=tools,
        messages=messages,
    )

# --- Step 2: final text answer, now grounded in real data ---
final_text = "".join(block.text for block in response.content if block.type == "text")
print("\nBean Counter:", final_text)
