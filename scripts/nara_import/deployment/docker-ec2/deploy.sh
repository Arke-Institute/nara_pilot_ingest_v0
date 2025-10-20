#!/bin/bash
# NARA Import - Docker EC2 Deployment
#
# Usage:
#   ./deploy.sh              # Interactive mode (test import)
#   ./deploy.sh test         # Test import (3 records)
#   ./deploy.sh full         # Full import (2,053 records)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }

# Get mode
MODE=${1:-test}
if [ "$MODE" != "test" ] && [ "$MODE" != "full" ]; then
    print_error "Invalid mode: $MODE (use 'test' or 'full')"
    exit 1
fi

echo "========================================="
echo "NARA Import - Docker EC2 Deployment"
echo "========================================="
echo "Mode: $MODE"
echo ""

# Check prerequisites
print_step "Checking prerequisites..."
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI not configured"
    exit 1
fi

if ! command -v rsync &> /dev/null; then
    print_error "rsync not found"
    exit 1
fi

print_success "Prerequisites met"
echo ""

# AWS Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
INSTANCE_NAME="nara-import-$(date +%Y%m%d-%H%M%S)"
KEY_NAME="nara-import-key-$(date +%Y%m%d)"
KEY_FILE="$HOME/.ssh/${KEY_NAME}.pem"

print_step "Setting up AWS resources..."

# Get latest Ubuntu AMI
AMI_ID=$(aws ec2 describe-images \
    --region $AWS_REGION \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
              "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

# Get VPC/Subnet
VPC_ID=$(aws ec2 describe-vpcs \
    --region $AWS_REGION \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text)

SUBNET_ID=$(aws ec2 describe-subnets \
    --region $AWS_REGION \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[0].SubnetId' \
    --output text)

# Create key pair if needed
if ! aws ec2 describe-key-pairs --region $AWS_REGION --key-names $KEY_NAME &> /dev/null; then
    aws ec2 create-key-pair \
        --region $AWS_REGION \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > $KEY_FILE
    chmod 400 $KEY_FILE
    print_success "SSH key created: $KEY_FILE"
else
    print_info "Using existing SSH key: $KEY_FILE"
    if [ ! -f "$KEY_FILE" ]; then
        print_error "Key exists in AWS but not found locally at: $KEY_FILE"
        exit 1
    fi
fi

# Create/get security group
SG_NAME="nara-import-sg"
EXISTING_SG=$(aws ec2 describe-security-groups \
    --region $AWS_REGION \
    --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [ "$EXISTING_SG" != "None" ] && [ ! -z "$EXISTING_SG" ]; then
    SG_ID=$EXISTING_SG
    print_info "Using existing security group"
else
    SG_ID=$(aws ec2 create-security-group \
        --region $AWS_REGION \
        --group-name $SG_NAME \
        --description "NARA Import - SSH access" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)
    print_success "Security group created"
fi

# Ensure SSH rule exists
if ! aws ec2 describe-security-groups --group-ids $SG_ID --region $AWS_REGION \
    --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]' --output text | grep -q "22"; then
    aws ec2 authorize-security-group-ingress \
        --region $AWS_REGION \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 > /dev/null
    print_success "SSH access enabled"
fi

# Launch instance
print_step "Launching EC2 instance..."

INSTANCE_ID=$(aws ec2 run-instances \
    --region $AWS_REGION \
    --image-id $AMI_ID \
    --instance-type t3.small \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --subnet-id $SUBNET_ID \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=10,VolumeType=gp3}' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Mode,Value=$MODE}]" \
    --user-data file://$SCRIPT_DIR/user-data.sh \
    --query 'Instances[0].InstanceId' \
    --output text)

print_success "Instance launched: $INSTANCE_ID"

# Wait for instance
print_info "Waiting for instance to be ready..."
aws ec2 wait instance-running --region $AWS_REGION --instance-ids $INSTANCE_ID

PUBLIC_IP=$(aws ec2 describe-instances \
    --region $AWS_REGION \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

print_success "Instance running at: $PUBLIC_IP"
echo ""

# Wait for SSH and Docker
print_info "Waiting for SSH and Docker (60 seconds)..."
sleep 60

SSH_OPTS="-i $KEY_FILE -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

# Test SSH connection
MAX_RETRIES=10
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if ssh $SSH_OPTS ubuntu@$PUBLIC_IP "echo 'ready'" &> /dev/null; then
        print_success "SSH connection established"
        break
    else
        RETRY=$((RETRY+1))
        if [ $RETRY -lt $MAX_RETRIES ]; then
            print_info "Retrying SSH connection ($RETRY/$MAX_RETRIES)..."
            sleep 5
        else
            print_error "Could not establish SSH connection"
            exit 1
        fi
    fi
done
echo ""

# Upload project files
print_step "Uploading project files..."
ssh $SSH_OPTS ubuntu@$PUBLIC_IP 'mkdir -p ~/nara-import'

rsync -avz --progress \
    -e "ssh $SSH_OPTS" \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '*.log' \
    --exclude 'sample_records.json' \
    --exclude '.git' \
    --exclude 'deployment/ec2' \
    --exclude 'deployment/aws-batch' \
    "$PROJECT_DIR/" \
    ubuntu@$PUBLIC_IP:~/nara-import/

print_success "Files uploaded"
echo ""

# Build Docker image
print_step "Building Docker image on EC2..."
ssh $SSH_OPTS ubuntu@$PUBLIC_IP <<'BUILD'
set -e
cd ~/nara-import
echo "Building Docker image..."
docker build -t nara-import -f deployment/docker/Dockerfile . 2>&1 | tail -5
BUILD

print_success "Docker image built"
echo ""

# Start container in detached mode
print_step "Starting import container (mode: $MODE)..."
if [ "$MODE" = "full" ]; then
    SCRIPT="import_full_collection.py"
else
    SCRIPT="test_import_sample.py"
fi

ssh $SSH_OPTS ubuntu@$PUBLIC_IP <<RUN
cd ~/nara-import
docker run -d --name nara-import nara-import python $SCRIPT
RUN

print_success "Container started in background"
echo ""

# Save connection info
INFO_FILE="$SCRIPT_DIR/.instance-$INSTANCE_ID.info"
cat > $INFO_FILE <<EOF
INSTANCE_ID=$INSTANCE_ID
PUBLIC_IP=$PUBLIC_IP
KEY_FILE=$KEY_FILE
REGION=$AWS_REGION
MODE=$MODE
SCRIPT=$SCRIPT
LAUNCHED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo ""
echo "========================================="
echo "Import Started!"
echo "========================================="
echo "Instance ID:  $INSTANCE_ID"
echo "Region:       $AWS_REGION"
echo "Mode:         $MODE"
echo "IP Address:   $PUBLIC_IP"
echo ""
print_info "The container is running in the background on EC2."
echo ""
echo "Check status:"
echo -e "  ${BLUE}./check.sh $INSTANCE_ID${NC}"
echo ""
echo "Monitor continuously:"
echo -e "  ${BLUE}./monitor.sh $INSTANCE_ID${NC}"
echo ""
echo "When done, shutdown with:"
echo -e "  ${BLUE}./check.sh $INSTANCE_ID --shutdown${NC}"
echo ""
echo "Connection info saved to: $INFO_FILE"
echo ""
