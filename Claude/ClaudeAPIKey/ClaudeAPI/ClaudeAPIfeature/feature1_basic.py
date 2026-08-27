#!/usr/bin/env python3
"""
Feature 1: Basic Message (Single-Turn)
Demonstrates the simplest possible API call — no history, no system prompt.

Run:
    python feature1_basic.py
"""

from anthropic import AnthropicVertex

# Initialize client using Google Cloud credentials (no API key needed)
client = AnthropicVertex(
    project_id="learning-development-c-000027",
    region="us-east5",
)

# Send a single message to Claude
response = client.messages.create(
    model="claude-haiku-4-5@20251001",
    max_tokens=512,
    messages=[
        {
            "role": "user",
            "content": "what is the formula to calculate surface area of circle "
        }
    ]
)

print(response.content[0].text)
