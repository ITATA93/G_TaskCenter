#!/bin/bash
# parallel-agents.sh — Launch sub-agents in parallel
# Usage: ./parallel-agents.sh "task1|agent1" "task2|agent2" ...
# Example: ./parallel-agents.sh "Analyze code|code-analyst" "Update README|doc-writer"

set -uo pipefail

LOGS_DIR=".gemini/agents/logs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "$LOGS_DIR"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"task|agent\" \"task|agent\" ..."
    echo "   Agents: code-analyst, doc-writer, code-reviewer, test-writer, db-analyst, deployer"
    exit 1
fi

echo "Launching $# sub-agent(s) in parallel..."
echo ""

PIDS=()
AGENTS=()

for TASK_SPEC in "$@"; do
    TASK=$(echo "$TASK_SPEC" | cut -d'|' -f1)
    AGENT=$(echo "$TASK_SPEC" | cut -d'|' -f2)

    LOG_FILE="$LOGS_DIR/${AGENT}-${TIMESTAMP}.log"

    gemini -p "You are the '$AGENT' agent. Your ONLY task is: $TASK. Work in the current directory. When finished, write a summary of your work. Be concise and efficient." \
        --yolo --sandbox seatbelt \
        > "$LOG_FILE" 2>&1 &

    PID=$!
    PIDS+=($PID)
    AGENTS+=("$AGENT")
    echo "  > $AGENT (PID $PID) -> $TASK"
done

echo ""
echo "Waiting for all to complete..."
echo ""

# Wait and report
RESULTS=()
for i in "${!PIDS[@]}"; do
    wait "${PIDS[$i]}"
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        RESULTS+=("[OK] ${AGENTS[$i]}")
        echo "  [OK] ${AGENTS[$i]} completed successfully"
    else
        RESULTS+=("[FAIL] ${AGENTS[$i]} (exit: $EXIT_CODE)")
        echo "  [FAIL] ${AGENTS[$i]} failed (exit: $EXIT_CODE)"
    fi
done

echo ""
echo "======================================="
echo "PARALLEL EXECUTION SUMMARY"
echo "   Timestamp: $TIMESTAMP"
echo "======================================="
for R in "${RESULTS[@]}"; do
    echo "  $R"
done
echo ""
echo "Logs: $LOGS_DIR/*-${TIMESTAMP}*"
echo "======================================="
