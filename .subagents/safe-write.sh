#!/bin/bash
# safe-write.sh - Output Governance File Creator
# Ensures that files are created in the allowed target directories matching Antigravity standards.

TARGET_FILE="$1"

if [ -z "$TARGET_FILE" ]; then
    echo "Usage: ./safe-write.sh <path/to/file.ext>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

# Convert to absolute path if needed, or assume relative to workspace root
if [[ "$TARGET_FILE" != /* ]]; then
    TARGET_FILE="$WORKSPACE_ROOT/$TARGET_FILE"
fi

# Define allowed zones (Output Governance)
ALLOWED_ZONES=(
    "$WORKSPACE_ROOT/docs/audit"
    "$WORKSPACE_ROOT/docs/plans"
    "$WORKSPACE_ROOT/docs/research"
    "$WORKSPACE_ROOT/docs/decisions"
    "$WORKSPACE_ROOT/scripts/temp"
    "$WORKSPACE_ROOT/.gemini/skills"
    "$WORKSPACE_ROOT/.claude/skills"
    "$WORKSPACE_ROOT/.agent/workflows"
)

# Exception Check for Root Files
BASENAME=$(basename "$TARGET_FILE")
ROOT_EXCEPTIONS=("GEMINI.md" "CLAUDE.md" "AGENTS.md" "CHANGELOG.md" "README.md" "DEVLOG.md" "TASKS.md")

IS_ROOT_EXCEPTION=0
for exc in "${ROOT_EXCEPTIONS[@]}"; do
    if [ "$BASENAME" == "$exc" ]; then
        if [ "$(dirname "$TARGET_FILE")" == "$WORKSPACE_ROOT" ] || [ "$(dirname "$TARGET_FILE")" == "$WORKSPACE_ROOT/docs" ]; then
            IS_ROOT_EXCEPTION=1
            break
        fi
    fi
done

# Check if target is in an allowed zone
IS_ALLOWED=0
for zone in "${ALLOWED_ZONES[@]}"; do
    if [[ "$TARGET_FILE" == "$zone"* ]]; then
        IS_ALLOWED=1
        break
    fi
done

if [ $IS_ALLOWED -eq 0 ] && [ $IS_ROOT_EXCEPTION -eq 0 ]; then
    # In src/ or tests/ it usually is fine, but we warn about arbitrary markdown files missing governance
    if [[ "$TARGET_FILE" == "$WORKSPACE_ROOT/src"* ]] || [[ "$TARGET_FILE" == "$WORKSPACE_ROOT/tests"* ]]; then
        IS_ALLOWED=1
    else
        echo -e "\033[0;31m[GOVERNANCE ERROR]\033[0m Cannot auto-create file: $TARGET_FILE"
        echo "Does not match allowed output governance zones (docs/audit, docs/plans, etc.)."
        exit 1
    fi
fi

# Create directory tree safely
TARGET_DIR=$(dirname "$TARGET_FILE")
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
    echo -e "\033[0;32m[GOVERNANCE PASS]\033[0m Auto-created directory tree: $TARGET_DIR"
fi

# Write empty file if it doesn't exist to reserve it
if [ ! -f "$TARGET_FILE" ]; then
    touch "$TARGET_FILE"
    echo -e "\033[0;32m[GOVERNANCE PASS]\033[0m Secured and created file pointer -> $TARGET_FILE"
else
    echo -e "\033[0;33m[GOVERNANCE WARN]\033[0m Target file already exists, skipping creation -> $TARGET_FILE"
fi

exit 0
