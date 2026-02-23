# Workflow: Parallel Agent Execution

## Purpose
Execute multiple sub-agents simultaneously for independent tasks.

## Requirements
- Tasks must be INDEPENDENT (no shared file modifications)
- Maximum 4 agents in parallel
- Each agent gets isolated scope

## Execution Pattern

### 1. Task Decomposition
Analyze request and split into independent tasks:
```
Request: "Add user auth with tests and docs"

Tasks:
1. Design auth flow → code-analyst
2. Write auth tests → test-writer
3. Document API → doc-writer
```

### 2. Launch Script
```bash
#!/bin/bash
# parallel-agents.sh

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOGS_DIR=".gemini/agents/logs"

# Launch each agent in background
gemini -e code-analyst -p "Task 1" --yolo --sandbox seatbelt \
  > "$LOGS_DIR/analyst-$TIMESTAMP.log" 2>&1 &
PID1=$!

gemini -e test-writer -p "Task 2" --yolo --sandbox seatbelt \
  > "$LOGS_DIR/tester-$TIMESTAMP.log" 2>&1 &
PID2=$!

gemini -e doc-writer -p "Task 3" --yolo --sandbox seatbelt \
  > "$LOGS_DIR/writer-$TIMESTAMP.log" 2>&1 &
PID3=$!

# Wait for all to complete
wait $PID1 $PID2 $PID3

# Aggregate results
echo "All agents completed. Check logs in $LOGS_DIR"
```

### 3. Result Aggregation
```
- Read all log files
- Verify no conflicts
- Present consolidated summary
- Handle any failures
```

## Conflict Prevention
```
Agent 1: src/api/**
Agent 2: tests/**
Agent 3: docs/**
```

## Error Handling
- If agent fails: log error, continue others
- If conflict detected: stop and report
- Manual resolution may be required
