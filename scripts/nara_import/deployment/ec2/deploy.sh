#!/bin/bash
# EC2 Deployment Script for NARA Import
# Creates SSH key, launches spot instance, runs import with auto-shutdown

set -e

# Configuration
REGION="${AWS_REGION:-us-east-1}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.small}"
KEY_NAME="nara-import-key-$(date +%Y%m%d)"
KEY_PATH="$HOME/.ssh/$KEY_NAME.pem"
INSTANCE_NAME="nara-import-$(date +%Y%m%d-%H%M%S)"
AMI_ID="${AMI_ID:-ami-0c398cb65a93047f2}"  # Ubuntu 22.04 LTS for us-east-1 (Oct 2025)
MODE="${1:-test}"  # test or full

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NARA Import - EC2 Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Mode: $MODE"
echo "Instance Name: $INSTANCE_NAME"
echo ""

# 1. Create SSH key pair if it doesn't exist
echo -e "${YELLOW}[1/6] Setting up SSH key pair...${NC}"

# Ensure ~/.ssh directory exists
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "✓ Key pair '$KEY_NAME' already exists in AWS"
    if [ ! -f "$KEY_PATH" ]; then
        echo -e "${YELLOW}Warning: Key pair exists in AWS but not found locally at: $KEY_PATH${NC}"
        echo "You may need to use an existing key or delete the AWS key pair and re-run."
    fi
else
    echo "Creating new key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --region "$REGION" \
        --query 'KeyMaterial' \
        --output text > "$KEY_PATH"

    chmod 400 "$KEY_PATH"
    echo -e "${GREEN}✓ Created key pair and saved to: $KEY_PATH${NC}"
fi

# 2. Get default VPC and subnet
echo -e "${YELLOW}[2/6] Getting VPC configuration...${NC}"
DEFAULT_VPC=$(aws ec2 describe-vpcs \
    --region "$REGION" \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text)

DEFAULT_SUBNET=$(aws ec2 describe-subnets \
    --region "$REGION" \
    --filters "Name=vpc-id,Values=$DEFAULT_VPC" \
    --query 'Subnets[0].SubnetId' \
    --output text)

echo "✓ VPC: $DEFAULT_VPC"
echo "✓ Subnet: $DEFAULT_SUBNET"

# 3. Create security group (or use existing)
echo -e "${YELLOW}[3/6] Setting up security group...${NC}"
SG_NAME="nara-import-sg"
SG_ID=$(aws ec2 describe-security-groups \
    --region "$REGION" \
    --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$DEFAULT_VPC" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [ "$SG_ID" = "None" ]; then
    echo "Creating security group: $SG_NAME"
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SG_NAME" \
        --description "NARA Import - SSH access only" \
        --vpc-id "$DEFAULT_VPC" \
        --region "$REGION" \
        --output text)

    echo -e "${GREEN}✓ Created security group: $SG_ID${NC}"
else
    echo "✓ Using existing security group: $SG_ID"
fi

# Ensure SSH access is enabled (add rule if it doesn't exist)
if ! aws ec2 describe-security-groups --group-ids "$SG_ID" --region "$REGION" \
    --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]' --output text | grep -q "22"; then
    echo "Adding SSH ingress rule..."
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$REGION" >/dev/null
    echo "✓ SSH access enabled"
fi

# 4. Select user-data script
echo -e "${YELLOW}[4/6] Preparing user-data script...${NC}"
if [ "$MODE" = "full" ]; then
    USER_DATA_SCRIPT="user-data-full.sh"
    echo "Selected: Full import (2,053 file units, 4-8 hours)"
else
    USER_DATA_SCRIPT="user-data-test.sh"
    echo "Selected: Test import (3 records, ~1 minute)"
fi

if [ ! -f "$USER_DATA_SCRIPT" ]; then
    echo -e "${RED}✗ User data script not found: $USER_DATA_SCRIPT${NC}"
    exit 1
fi

# 5. Launch EC2 spot instance
echo -e "${YELLOW}[5/6] Launching EC2 spot instance...${NC}"

INSTANCE_ID=$(aws ec2 run-instances \
    --region "$REGION" \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --subnet-id "$DEFAULT_SUBNET" \
    --instance-market-options '{"MarketType":"spot","SpotOptions":{"SpotInstanceType":"one-time"}}' \
    --user-data "file://$USER_DATA_SCRIPT" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Project,Value=NARA-Import},{Key=Mode,Value=$MODE}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo -e "${GREEN}✓ Instance launched: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo -e "${GREEN}✓ Instance is running${NC}"
echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP: $PUBLIC_IP"

# 6. Display connection info and monitoring
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Instance Details:"
echo "  ID: $INSTANCE_ID"
echo "  IP: $PUBLIC_IP"
echo "  Key: $KEY_PATH"
echo "  Mode: $MODE"
echo ""
echo "SSH Connection:"
echo "  ssh -i $KEY_PATH ubuntu@$PUBLIC_IP"
echo ""
echo "Monitor Progress:"
echo "  ssh -i $KEY_PATH ubuntu@$PUBLIC_IP 'tail -f /var/log/nara-import.log'"
echo ""
echo "Check Instance Status:"
echo "  aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION --query 'Reservations[0].Instances[0].State.Name' --output text"
echo ""

if [ "$MODE" = "test" ]; then
    echo -e "${YELLOW}Test Mode:${NC}"
    echo "  - Import will complete in ~2-3 minutes"
    echo "  - Instance will auto-shutdown 60 seconds after completion"
    echo "  - Verify auto-shutdown works before running full import"
    echo ""
    echo "Next Steps:"
    echo "  1. Wait 5 minutes for test to complete and instance to shutdown"
    echo "  2. Verify instance state: aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name'"
    echo "  3. If successful, run full import: ./deploy.sh full"
else
    echo -e "${YELLOW}Full Import Mode:${NC}"
    echo "  - Import will take 4-8 hours"
    echo "  - Instance will auto-shutdown after completion"
    echo "  - Progress is saved every 10 records (can resume if interrupted)"
    echo ""
    echo "Monitoring:"
    echo "  - SSH in to check progress (tmux will keep session alive)"
    echo "  - Check logs: import_full_*.log"
    echo "  - Instance auto-terminates on completion"
fi

echo ""
echo -e "${GREEN}========================================${NC}"

# Save instance info to file
cat > ".instance-$INSTANCE_ID.info" <<EOINFO
INSTANCE_ID=$INSTANCE_ID
PUBLIC_IP=$PUBLIC_IP
KEY_NAME=$KEY_NAME
KEY_PATH=$KEY_PATH
REGION=$REGION
MODE=$MODE
LAUNCHED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOINFO

echo "Instance info saved to: .instance-$INSTANCE_ID.info"
echo ""
