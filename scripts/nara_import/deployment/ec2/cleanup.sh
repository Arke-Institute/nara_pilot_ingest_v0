#!/bin/bash
# Cleanup Script - Terminate instances and remove resources

set -e

REGION="${AWS_REGION:-us-east-1}"
MODE="${1:-}"

echo "========================================="
echo "NARA Import - Cleanup"
echo "========================================="
echo ""

if [ -z "$MODE" ]; then
    echo "Usage: ./cleanup.sh [all|<instance-id>]"
    echo ""
    echo "Examples:"
    echo "  ./cleanup.sh all              # Terminate all NARA import instances"
    echo "  ./cleanup.sh i-1234567890     # Terminate specific instance"
    echo ""
    exit 1
fi

if [ "$MODE" = "all" ]; then
    echo "Finding all NARA import instances..."
    INSTANCE_IDS=$(aws ec2 describe-instances \
        --region "$REGION" \
        --filters "Name=tag:Project,Values=NARA-Import" "Name=instance-state-name,Values=running,stopped,pending,stopping" \
        --query 'Reservations[].Instances[].InstanceId' \
        --output text)
    
    if [ -z "$INSTANCE_IDS" ]; then
        echo "No NARA import instances found"
        exit 0
    fi
    
    echo "Found instances: $INSTANCE_IDS"
    echo ""
    read -p "Terminate these instances? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
    
    for INSTANCE_ID in $INSTANCE_IDS; do
        echo "Terminating: $INSTANCE_ID"
        aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --region "$REGION" >/dev/null
    done
    
    echo ""
    echo "✓ All instances terminated"
    
    # Clean up info files
    echo "Cleaning up instance info files..."
    rm -f .instance-*.info
    
else
    # Terminate specific instance
    INSTANCE_ID="$MODE"
    echo "Terminating instance: $INSTANCE_ID"
    
    aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --region "$REGION"
    
    echo "✓ Instance $INSTANCE_ID terminated"
    
    # Clean up info file
    rm -f ".instance-$INSTANCE_ID.info"
fi

echo ""
echo "Note: Security group and key pairs are NOT deleted"
echo "To remove manually:"
echo "  aws ec2 delete-security-group --group-name nara-import-sg --region $REGION"
echo "  aws ec2 delete-key-pair --key-name nara-import-key-YYYYMMDD --region $REGION"
echo ""
