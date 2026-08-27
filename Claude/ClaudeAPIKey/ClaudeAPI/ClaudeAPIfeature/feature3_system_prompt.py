#!/usr/bin/env python3
"""
Feature 3: System Prompts
Demonstrates using a system prompt to give Claude a persistent role,
tone, and set of ground rules — separate from the conversation itself.

Run:
    python feature3_system_prompt.py
"""

from anthropic import AnthropicVertex

client = AnthropicVertex(
    project_id="learning-development-c-000027",
    region="us-east5",
)

MODEL = "claude-haiku-4-5@20251001"

# The system prompt shapes HOW Claude answers, for every turn, without
# needing to repeat instructions in each user message.
SYSTEM_PROMPT = """You are "Bean Counter", the AI financial analyst for
BrewCo, a US coffee shop chain. Rules you always follow:
- Speak to a small-business owner, not an accountant — avoid jargon.
- Always give concrete numbers or percentages when possible.
- Keep answers under 100 words unless asked for more detail.
- If you don't have enough information, say so plainly instead of guessing.
"""

response = client.messages.create(
    model=MODEL,
    max_tokens=400,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": "Our wages are 35% of revenue. Is that normal for a "
                       "coffee shop?"
        }
    ]
)

print(response.content[0].text)

print("\n--- Compare: same question, no system prompt ---\n")

response_plain = client.messages.create(
    model=MODEL,
    max_tokens=400,
    messages=[
        {
            "role": "user",
            "content": "Our wages are 35% of revenue. Is that normal for a "
                       "coffee shop?"
        }
    ]
)

print(response_plain.content[0].text)
