#!/usr/bin/env python3
"""
Feature 4: Streaming Responses
Demonstrates streaming the reply token-by-token instead of waiting for the
full response — this is what makes a UI feel fast/live (e.g. the chat tab
in the Streamlit app).

Run:
    python feature4_streaming.py
"""

from anthropic import AnthropicVertex

client = AnthropicVertex(
    project_id="learning-development-c-000027",
    region="us-east5",
)

MODEL = "claude-haiku-4-5@20251001"

SYSTEM_PROMPT = "You are Bean Counter, BrewCo's financial analyst. Be concise."

print("Bean Counter: ", end="", flush=True)

with client.messages.stream(
    model=MODEL,
    max_tokens=500,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": "Write a 3-bullet summary of why streaming responses "
                       "feel faster to users even though the total time is "
                       "about the same."
        }
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n\n(Done — that printed as it arrived, rather than all at once.)")
