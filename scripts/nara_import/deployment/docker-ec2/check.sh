#!/bin/bash
# Check status of NARA import instance and container

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANCE_ID=$1
SHUTDOWN_FLAG=$2
REGION=${AWS_REGION:-us-east-1}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

if [ -z "$INSTANCE_ID" ]; then
    echo "Usage: ./check.sh <instance-id> [--shutdown]"
    echo ""
    echo "Options:"
    echo "  --shutdown    Shutdown instance if import is complete"
    echo ""
    echo "Available instances:"
    aws ec2 describe-instances \
        --region $REGION \
        --filters "Name=tag:Name,Values=nara-import-*" "Name=instance-state-name,Values=running,pending,stopping,stopped" \
        --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress,Tags[?Key==`Mode`].Value|[0],LaunchTime]' \
        --output table
    exit 1
fi

# Get instance info
INSTANCE_INFO=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0]' \
    --output json 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$INSTANCE_INFO" ]; then
    echo -e "${RED}✗ Instance not found: $INSTANCE_ID${NC}"
    exit 1
fi

STATE=$(echo "$INSTANCE_INFO" | jq -r '.State.Name')
PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress // "N/A"')
MODE=$(echo "$INSTANCE_INFO" | jq -r '.Tags[] | select(.Key=="Mode") | .Value')
LAUNCH_TIME=$(echo "$INSTANCE_INFO" | jq -r '.LaunchTime')

# Calculate uptime
if [ "$LAUNCH_TIME" != "null" ]; then
    LAUNCH_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAUNCH_TIME%.*}" +%s 2>/dev/null || date -d "${LAUNCH_TIME}" +%s 2>/dev/null)
    NOW_EPOCH=$(date +%s)
    UPTIME_SEC=$((NOW_EPOCH - LAUNCH_EPOCH))
    UPTIME_MIN=$((UPTIME_SEC / 60))
    UPTIME_DISPLAY="${UPTIME_MIN}m"
else
    UPTIME_DISPLAY="unknown"
fi

echo ""
echo "========================================="
echo -e "${CYAN}Instance: $INSTANCE_ID${NC}"
echo "========================================="
echo -e "State:    ${YELLOW}$STATE${NC}"
echo "IP:       $PUBLIC_IP"
echo "Mode:     $MODE"
echo "Uptime:   $UPTIME_DISPLAY"
echo "========================================="
echo ""

# Try to get key file from saved info
INFO_FILE="$SCRIPT_DIR/.instance-$INSTANCE_ID.info"
if [ ! -f "$INFO_FILE" ]; then
    echo -e "${YELLOW}⚠ No saved connection info found${NC}"
    echo "This instance may have been launched by a different deployment."
    exit 1
fi

source "$INFO_FILE"

if [ "$STATE" = "stopped" ]; then
    echo -e "${GREEN}✓ Instance has stopped (import complete)${NC}"
    exit 0
elif [ "$STATE" = "terminated" ]; then
    echo -e "${RED}Instance has been terminated${NC}"
    exit 0
elif [ "$STATE" != "running" ]; then
    echo -e "${YELLOW}Instance state: $STATE${NC}"
    exit 0
fi

# Instance is running, check container
SSH_OPTS="-i $KEY_FILE -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=5"

echo -e "${BLUE}▶ Container Status${NC}"
CONTAINER_STATUS=$(ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'docker ps -a --filter name=nara-import --format "{{.Status}}"' 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Could not connect via SSH${NC}"
    exit 1
fi

if [ -z "$CONTAINER_STATUS" ]; then
    echo -e "${YELLOW}⚠ Container not found (may still be starting)${NC}"
    exit 0
fi

echo "$CONTAINER_STATUS"
echo ""

# Check if container is done
if echo "$CONTAINER_STATUS" | grep -q "Exited"; then
    EXIT_CODE=$(ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'docker inspect nara-import --format="{{.State.ExitCode}}"' 2>/dev/null)

    echo "========================================="
    if [ "$EXIT_CODE" = "0" ]; then
        echo -e "${GREEN}✓ Import Complete! (exit code: 0)${NC}"
    else
        echo -e "${RED}✗ Import Failed (exit code: $EXIT_CODE)${NC}"
    fi
    echo "========================================="
    echo ""

    # Show final logs
    echo -e "${BLUE}▶ Final Logs (last 50 lines)${NC}"
    echo "========================================="
    LOGS=$(ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'docker logs --tail 50 nara-import 2>&1')
    if [ -z "$LOGS" ]; then
        echo "(No logs available)"
    else
        echo "$LOGS"
    fi
    echo "========================================="
    echo ""

    # Shutdown prompt or auto-shutdown
    if [ "$SHUTDOWN_FLAG" = "--shutdown" ]; then
        echo -e "${YELLOW}Shutting down instance...${NC}"
        ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'sudo shutdown -h now' 2>/dev/null || true
        echo -e "${GREEN}✓ Shutdown command sent${NC}"
    else
        echo -e "${YELLOW}Shutdown instance?${NC} (y/n): "
        read -r RESPONSE
        if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
            echo "Sending shutdown command..."
            ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'sudo shutdown -h now' 2>/dev/null || true
            echo -e "${GREEN}✓ Shutdown command sent${NC}"
        else
            echo "Instance left running."
            echo ""
            echo "Shutdown later with:"
            echo "  ./check.sh $INSTANCE_ID --shutdown"
            echo "Or terminate:"
            echo "  ./cleanup.sh $INSTANCE_ID"
        fi
    fi
else
    # Container still running, show live logs
    echo -e "${BLUE}▶ Container Logs (last 50 lines)${NC}"
    echo "========================================="
    LOGS=$(ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'docker logs --tail 50 nara-import 2>&1')
    if [ -z "$LOGS" ]; then
        echo "(No logs yet - container just started)"
    else
        echo "$LOGS"
    fi
    echo "========================================="
    echo ""
    echo -e "${YELLOW}Import still running...${NC}"
    echo ""
    echo "Check again:"
    echo "  ./check.sh $INSTANCE_ID"
    echo ""
    echo "Monitor continuously:"
    echo "  ./monitor.sh $INSTANCE_ID"
    echo ""
    echo "View all logs:"
    echo "  ssh -i $KEY_FILE ubuntu@$PUBLIC_IP 'docker logs -f nara-import'"
fi

echo ""
