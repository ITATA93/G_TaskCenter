#!/bin/bash
# auto-memory.sh - Automatically updates DEVLOG after team execution

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DEVLOG_PATH="$WORKSPACE_ROOT/docs/DEVLOG.md"
TEAM_NAME="$1"
PROMPT="$2"

if [ ! -f "$DEVLOG_PATH" ]; then
    mkdir -p "$(dirname "$DEVLOG_PATH")"
    echo "# Development Log" > "$DEVLOG_PATH"
fi

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

cat << EOF >> "$DEVLOG_PATH"

## [Auto-Memory] Team Execution: $TEAM_NAME
**Date**: $TIMESTAMP
**Task**: $PROMPT
**Result**: Completed successfully.
EOF

echo "[MEMORY INFO] DEVLOG.md updated autonomously."
