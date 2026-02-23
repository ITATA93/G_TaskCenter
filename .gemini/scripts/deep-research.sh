#!/bin/bash
# deep-research.sh — Execute Gemini Deep Research via API
# Usage: ./deep-research.sh "your research question"
# Requires: GEMINI_API_KEY environment variable

set -euo pipefail

API_KEY="${GEMINI_API_KEY:-}"
QUERY="$1"
OUTPUT_DIR="docs/research"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

if [ -z "$API_KEY" ]; then
    echo "Error: GEMINI_API_KEY not configured"
    echo "   Run: export GEMINI_API_KEY='your-api-key'"
    exit 1
fi

if [ -z "$QUERY" ]; then
    echo "Error: Research query missing"
    echo "   Usage: $0 \"your question\""
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Launching Deep Research..."
echo "   Query: $QUERY"

# Start research
RESPONSE=$(curl -s -X POST \
    "https://generativelanguage.googleapis.com/v1beta/interactions" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: $API_KEY" \
    -d "{
        \"input\": \"$QUERY. Include cited sources.\",
        \"agent\": \"deep-research-pro-preview-12-2025\",
        \"background\": true
    }")

INTERACTION_ID=$(echo "$RESPONSE" | jq -r '.id // .name // empty')

if [ -z "$INTERACTION_ID" ]; then
    echo "Error starting research"
    echo "   Response: $RESPONSE"
    exit 1
fi

echo "   ID: $INTERACTION_ID"
echo "Researching (this takes 2-5 minutes)..."

# Poll until complete
ATTEMPTS=0
MAX_ATTEMPTS=40

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    RESULT=$(curl -s -X GET \
        "https://generativelanguage.googleapis.com/v1beta/interactions/$INTERACTION_ID" \
        -H "x-goog-api-key: $API_KEY")

    STATUS=$(echo "$RESULT" | jq -r '.status // "pending"')

    case "$STATUS" in
        "completed"|"COMPLETED")
            OUTPUT_FILE="$OUTPUT_DIR/research-${TIMESTAMP}.md"
            echo "# Deep Research: $QUERY" > "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "_Date: $(date +%Y-%m-%d\ %H:%M)_" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "---" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "$RESULT" | jq -r '.outputs[-1].text // .outputs[0].text // "No result"' >> "$OUTPUT_FILE"
            echo ""
            echo "Research completed"
            echo "Saved to: $OUTPUT_FILE"
            exit 0
            ;;
        "failed"|"FAILED")
            echo "Error: $(echo "$RESULT" | jq -r '.error // "Unknown error"')"
            exit 1
            ;;
        *)
            ATTEMPTS=$((ATTEMPTS + 1))
            echo -ne "   Waiting... ($((ATTEMPTS * 15))s)\r"
            sleep 15
            ;;
    esac
done

echo "Timeout: Research took more than 10 minutes"
exit 1
