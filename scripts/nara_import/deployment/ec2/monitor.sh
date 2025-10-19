#!/bin/bash
# Monitor NARA Import EC2 Instance

set -e

INSTANCE_ID="$1"
REGION="${AWS_REGION:-us-east-1}"

if [ -z "$INSTANCE_ID" ]; then
    echo "Usage: ./monitor.sh <instance-id>"
    echo ""
    echo "Available instances:"
    aws ec2 describe-instances \
        --region "$REGION" \
        --filters "Name=tag:Project,Values=NARA-Import" "Name=instance-state-name,Values=running,pending,stopping,stopped" \
        --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress,Tags[?Key==`Name`].Value|[0],Tags[?Key==`Mode`].Value|[0],LaunchTime]' \
        --output table
    exit 1
fi

# Get instance info
echo "Fetching instance details..."
INSTANCE_INFO=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION" \
    --query 'Reservations[0].Instances[0]' \
    --output json)

STATE=$(echo "$INSTANCE_INFO" | jq -r '.State.Name')
PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress // "N/A"')
LAUNCH_TIME=$(echo "$INSTANCE_INFO" | jq -r '.LaunchTime')
INSTANCE_TYPE=$(echo "$INSTANCE_INFO" | jq -r '.InstanceType')
MODE=$(echo "$INSTANCE_INFO" | jq -r '.Tags[] | select(.Key=="Mode") | .Value')

echo "========================================="
echo "Instance: $INSTANCE_ID"
echo "State: $STATE"
echo "IP: $PUBLIC_IP"
echo "Type: $INSTANCE_TYPE"
echo "Mode: $MODE"
echo "Launched: $LAUNCH_TIME"
echo "========================================="
echo ""

if [ "$STATE" = "running" ] && [ "$PUBLIC_IP" != "N/A" ]; then
    # Look for key file
    KEY_FILE=$(ls -t .instance-$INSTANCE_ID.info 2>/dev/null | head -1)
    if [ -f "$KEY_FILE" ]; then
        source "$KEY_FILE"

        echo "SSH Command:"
        echo "  ssh -i $KEY_PATH ubuntu@$PUBLIC_IP"
        echo ""
        echo "Tail Logs:"
        echo "  ssh -i $KEY_PATH ubuntu@$PUBLIC_IP 'tail -f /var/log/nara-import.log'"
        echo ""

        # Try to fetch recent log output
        echo "Recent Log Output (last 20 lines):"
        echo "-----------------------------------"
        ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@$PUBLIC_IP 'tail -20 /var/log/nara-import.log' 2>/dev/null || echo "Unable to fetch logs (instance may still be initializing)"
    else
        echo "Key file not found. SSH manually using:"
        echo "  ssh -i ~/.ssh/<your-key>.pem ubuntu@$PUBLIC_IP"
    fi
elif [ "$STATE" = "stopped" ]; then
    echo "Instance has stopped (auto-shutdown completed)"
    echo ""
    echo "To retrieve final logs, start instance temporarily:"
    echo "  aws ec2 start-instances --instance-ids $INSTANCE_ID --region $REGION"
    echo "  # Wait for running state, then SSH in"
elif [ "$STATE" = "terminated" ]; then
    echo "Instance has been terminated"
fi

echo ""
