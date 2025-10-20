#!/bin/bash
# Continuously monitor NARA import instance
# Polls every 30 seconds until container finishes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANCE_ID=$1
INTERVAL=${2:-30}  # Default 30 seconds

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ -z "$INSTANCE_ID" ]; then
    echo "Usage: ./monitor.sh <instance-id> [interval-seconds]"
    echo ""
    echo "Default interval: 30 seconds"
    echo ""
    echo "Example:"
    echo "  ./monitor.sh i-1234567890abcdef0"
    echo "  ./monitor.sh i-1234567890abcdef0 60  # Poll every 60 seconds"
    echo ""
    exit 1
fi

echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}NARA Import Monitor${NC}"
echo -e "${CYAN}=========================================${NC}"
echo "Instance:  $INSTANCE_ID"
echo "Interval:  ${INTERVAL}s"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo -e "${CYAN}=========================================${NC}"
echo ""

POLL_COUNT=0

while true; do
    POLL_COUNT=$((POLL_COUNT + 1))
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

    echo -e "${YELLOW}[Poll #$POLL_COUNT - $TIMESTAMP]${NC}"
    echo ""

    # Run check.sh and capture output
    OUTPUT=$($SCRIPT_DIR/check.sh $INSTANCE_ID 2>&1)
    EXIT_CODE=$?

    echo "$OUTPUT"

    # Check if container has finished
    if echo "$OUTPUT" | grep -q "Import Complete\|Import Failed"; then
        echo ""
        echo -e "${GREEN}=========================================${NC}"
        echo -e "${GREEN}Container finished!${NC}"
        echo -e "${GREEN}=========================================${NC}"
        echo ""
        echo "Run check.sh to shutdown:"
        echo "  ./check.sh $INSTANCE_ID"
        echo ""
        exit 0
    fi

    # Check if instance is stopped/terminated
    if echo "$OUTPUT" | grep -q "Instance has stopped\|Instance has been terminated"; then
        echo ""
        echo -e "${YELLOW}Instance no longer running${NC}"
        exit 0
    fi

    # Check if connection failed
    if echo "$OUTPUT" | grep -q "Could not connect\|Instance not found"; then
        echo ""
        echo -e "${RED}Connection failed or instance not found${NC}"
        echo "Retrying in ${INTERVAL}s..."
    fi

    echo ""
    echo -e "${CYAN}Next check in ${INTERVAL} seconds...${NC}"
    echo ""
    sleep $INTERVAL
done
