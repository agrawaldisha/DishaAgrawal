#!/bin/bash
# PreToolUse hook — runs BEFORE Claude edits/writes a file.
# Reads the tool call as JSON from stdin, and can block it by exiting with code 2.

input=$(cat)

# Pull the file path out of the JSON input (works for Edit/Write tools)
file_path=$(echo "$input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

# Block edits to .env files or anything in a "secrets" folder
if [[ "$file_path" == *".env"* ]] || [[ "$file_path" == *"/secrets/"* ]]; then
  echo "BLOCKED: Editing '$file_path' is not allowed by policy." >&2
  exit 2   # exit code 2 = block the action, message shown to Claude
fi

exit 0     # exit code 0 = allow the action
