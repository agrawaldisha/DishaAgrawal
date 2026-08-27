#!/bin/bash
# PostToolUse hook — runs AFTER Claude edits/writes a file.
# Simple audit log: appends every edited file + timestamp to a log file.

input=$(cat)

file_path=$(echo "$input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

log_file="$(dirname "$0")/../edit_log.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S')  edited: $file_path" >> "$log_file"

exit 0
