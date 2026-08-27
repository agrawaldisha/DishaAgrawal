#!/usr/bin/env python3
"""
Feature 2: Multi-Turn Conversation
Demonstrates maintaining conversation history so Claude has context from
earlier turns — this is what makes a "chat" feel like a chat.

Run:
    python feature2_multiturn.py
"""

from anthropic import AnthropicVertex

client = AnthropicVertex(
    project_id="learning-development-c-000027",
    region="us-east5",
)

MODEL = "claude-haiku-4-5@20251001"

# The conversation history is just a growing list of {"role", "content"} dicts.
# Every call sends the FULL history — Claude itself has no memory between calls.
history = []


def ask(question: str) -> str:
    history.append({"role": "user", "content": question})
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=history,
    )
    answer = response.content[0].text
    history.append({"role": "assistant", "content": answer})
    return answer


if __name__ == "__main__":
    print("Turn 1:")
    print(ask("BrewCo has 5 stores: Downtown, Uptown, Airport, Mall Kiosk, "
               "and University. The Airport store had a cost spike last month. "
               "What questions should I ask to diagnose it?"))

    print("\nTurn 2 (notice it remembers 'the Airport store' from turn 1):")
    print(ask("Good. Now which of those questions would you ask first, and why?"))

    print("\nTurn 3 (still using the same context):")
    print(ask("Summarize this whole conversation in one sentence for my notes."))
