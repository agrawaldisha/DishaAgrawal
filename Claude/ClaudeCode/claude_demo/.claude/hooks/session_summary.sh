#!/bin/bash
# Stop hook — runs when Claude finishes responding / the turn ends.
# Good spot for a desktop notification, Slack ping, or wrap-up summary.

hook_dir="$(dirname "$0")"
summary_file="$hook_dir/session_summary.log"
edit_log="$hook_dir/../edit_log.txt"

touch "$summary_file"

if [[ -f "$edit_log" ]]; then
  count=$(wc -l < "$edit_log" | tr -d ' ')
else
  count=0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - Session finished. $count file edit(s) logged so far." >> "$summary_file"

exit 0
