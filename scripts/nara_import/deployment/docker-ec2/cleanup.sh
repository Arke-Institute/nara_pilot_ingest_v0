#!/bin/bash
# Cleanup - Terminate NARA import instance

INSTANCE_ID=$1
REGION=${AWS_REGION:-us-east-1}

if [ -z "$INSTANCE_ID" ]; then
    echo "Usage: ./cleanup.sh <instance-id>"
    echo ""
    echo "Or use 'all' to terminate all NARA import instances:"
    echo "  ./cleanup.sh all"
    exit 1
fi

if [ "$INSTANCE_ID" = "all" ]; then
    echo "Finding all NARA import instances..."
    INSTANCE_IDS=$(aws ec2 describe-instances \
        --region $REGION \
        --filters "Name=tag:Name,Values=nara-import-*" "Name=instance-state-name,Values=running,stopped,pending,stopping" \
        --query 'Reservations[].Instances[].InstanceId' \
        --output text)
    
    if [ -z "$INSTANCE_IDS" ]; then
        echo "No NARA import instances found"
        exit 0
    fi
    
    echo "Found instances: $INSTANCE_IDS"
    read -p "Terminate all? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
    
    for ID in $INSTANCE_IDS; do
        echo "Terminating: $ID"
        aws ec2 terminate-instances --instance-ids $ID --region $REGION >/dev/null
    done
    
    echo "✓ All instances terminated"
    rm -f .instance-*.info
else
    echo "Terminating instance: $INSTANCE_ID"
    aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION
    echo "✓ Instance $INSTANCE_ID terminated"
    rm -f ".instance-$INSTANCE_ID.info"
fi

echo ""
