#!/bin/bash
#
# dispatch-team.sh - Multi-vendor Agent Team orchestrator
# Executes a group of agents sequentially or in parallel based on manifest.json
#
# Usage:
#   ./dispatch-team.sh <team_name> "<prompt>"
#
# Examples:
#   ./dispatch-team.sh full-review "Audit the auth module for security flaws"
#

set -e

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_PATH="$SCRIPT_DIR/manifest.json"
DISPATCH_SCRIPT="$SCRIPT_DIR/dispatch.sh"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# =============================================================================
# FUNCTIONS
# =============================================================================

log_info() { echo -e "${CYAN}[TEAM INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[TEAM WARN]${NC} $1"; }
log_error() { echo -e "${RED}[TEAM ERROR]${NC} $1" >&2; }
log_success() { echo -e "${GREEN}[TEAM OK]${NC} $1"; }

show_usage() {
    cat << EOF
Usage: $(basename "$0") <team_name> "<prompt>"

Arguments:
  team_name       Name of the team defined in manifest.json (e.g., full-review)
  prompt          The overall task for the team

Available teams:
$(jq -r '(.teams // .agent_teams.teams // {}) | keys[]' "$MANIFEST_PATH" 2>/dev/null | sed 's/^/  - /')
EOF
}

# =============================================================================
# MAIN
# =============================================================================

if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

TEAM_NAME="$1"
PROMPT="$2"

if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed."
    exit 1
fi

if [ ! -f "$MANIFEST_PATH" ]; then
    log_error "Manifest not found: $MANIFEST_PATH"
    exit 1
fi

if [ ! -x "$DISPATCH_SCRIPT" ]; then
    log_error "Dispatch script not found or not executable: $DISPATCH_SCRIPT"
    exit 1
fi

# Get team configuration
TEAM_CONFIG=$(jq -c "(.teams // .agent_teams.teams // {})[\"$TEAM_NAME\"]" "$MANIFEST_PATH" 2>/dev/null)

if [ -z "$TEAM_CONFIG" ] || [ "$TEAM_CONFIG" = "null" ]; then
    log_error "Team '$TEAM_NAME' not found in manifest"
    show_usage
    exit 1
fi

EXEC_MODE=$(echo "$TEAM_CONFIG" | jq -r '.mode // .execution // "sequential"')
AGENTS=$(echo "$TEAM_CONFIG" | jq -r '.agents[]')
AGENT_COUNT=$(echo "$AGENTS" | wc -w)

log_info "Deploying team: $TEAM_NAME ($EXEC_MODE execution - $AGENT_COUNT agents)"
echo ""

# Execute based on mode
declare -A PIDS

if [ "$EXEC_MODE" = "parallel" ]; then
    for AGENT in $AGENTS; do
        log_info "Starting agent $AGENT in background..."
        "$DISPATCH_SCRIPT" "$AGENT" "$PROMPT" &
        PIDS[$AGENT]=$!
    done

    log_info "Waiting for all parallel agents to complete..."
    FAILURES=0
    for AGENT in "${!PIDS[@]}"; do
        wait ${PIDS[$AGENT]}
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 0 ]; then
            log_success "Agent $AGENT completed successfully"
        else
            log_error "Agent $AGENT failed with exit code $EXIT_CODE"
            FAILURES=$((FAILURES + 1))
        fi
    done

    if [ $FAILURES -gt 0 ]; then
        log_error "Team execution finished with $FAILURES failures."
        exit 1
    fi

elif [ "$EXEC_MODE" = "sequential" ]; then
    for AGENT in $AGENTS; do
        log_info "Starting agent $AGENT..."
        "$DISPATCH_SCRIPT" "$AGENT" "$PROMPT"
        EXIT_CODE=$?

        if [ $EXIT_CODE -ne 0 ]; then
            log_error "Agent $AGENT failed. Halting sequential team execution."
            exit 1
        fi
        log_success "Agent $AGENT completed successfully"
        echo ""
    done
else
    log_error "Unknown execution mode: $EXEC_MODE"
    exit 1
fi

# Auto-Memory Hook
AUTO_MEM_SCRIPT="$SCRIPT_DIR/auto-memory.sh"
if [ -x "$AUTO_MEM_SCRIPT" ]; then
    "$AUTO_MEM_SCRIPT" "$TEAM_NAME" "$PROMPT"
fi

log_success "Team execution '$TEAM_NAME' completed successfully"
