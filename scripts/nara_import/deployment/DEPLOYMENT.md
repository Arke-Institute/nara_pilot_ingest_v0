# NARA Import Deployment Guide

This guide covers deploying the NARA collection importer to AWS for long-running batch processing without tying up your local machine.

## Overview

- **Runtime**: 4-8 hours for full collection (2,053 file units)
- **API**: Production Arke API at `https://api.arke.institute`
- **Workload**: I/O-bound (downloads from S3, API calls, hashing)
- **Auto-shutdown**: Script exits when complete - perfect for batch jobs
- **Checkpoint system**: Can resume if interrupted
- **Network**: Just needs internet access (no local API required!)

## Architecture Simplified

Since the Arke API runs remotely at `https://api.arke.institute`, deployment is very simple:

```
┌─────────────────────┐
│  AWS Compute        │
│  (Batch/ECS/EC2)    │
│                     │
│  ┌──────────────┐   │      HTTPS        ┌──────────────────┐
│  │ Import Script│───┼─────────────────▶ │ api.arke.institute│
│  └──────────────┘   │                   └──────────────────┘
│         │           │
│         ▼           │      AWS CLI
│  ┌──────────────┐   │   (no-sign-request)
│  │ Download     │───┼─────────────────▶ NARA S3 Bucket
│  │ & Hash       │   │
│  └──────────────┘   │
└─────────────────────┘
```

**No complex networking required!** The script just needs:
1. Internet access to call `https://api.arke.institute`
2. AWS CLI installed to download NARA metadata (public bucket, no credentials needed)

---

## Recommended Deployment Options

### Option 1: AWS Batch (Best for Production)

**Best for**: Managed batch jobs with auto-shutdown and retry logic

#### Why AWS Batch?
- ✅ **Auto-shutdown**: Job terminates when script exits (no manual cleanup)
- ✅ **Spot instances**: 70% cost savings
- ✅ **Automatic retries**: If job fails, Batch can retry automatically
- ✅ **CloudWatch integration**: Centralized logging
- ✅ **Perfect for this use case**: One-time long-running batch job

#### Setup Steps

**1. Build and push Docker image to ECR**

```bash
cd scripts/nara_import

# Build image
docker build -t nara-import .

# Create ECR repository
aws ecr create-repository --repository-name nara-import --region us-east-1

# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag nara-import:latest <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/nara-import:latest
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/nara-import:latest
```

**2. Create Batch compute environment** (via AWS Console or CLI)

```bash
# Using AWS Console (easier):
# 1. Go to AWS Batch → Compute environments → Create
# 2. Choose "Fargate" for serverless (recommended)
# 3. Enable "Use Fargate Spot capacity" for 70% cost savings
# 4. Set maximum vCPUs: 2 (this job only needs 1-2 vCPUs)
# 5. Create
```

**3. Create job queue**

```bash
# Using AWS Console:
# 1. Go to AWS Batch → Job queues → Create
# 2. Connect to your compute environment
# 3. Priority: 1
# 4. Create
```

**4. Create job definition**

```bash
# Using AWS Console:
# 1. Go to AWS Batch → Job definitions → Create
# 2. Platform: Fargate
# 3. Job definition name: nara-import
# 4. Image: <YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/nara-import:latest
# 5. vCPUs: 1
# 6. Memory: 2 GB (script uses <1GB, but 2GB provides headroom)
# 7. Job role: (optional) Create IAM role if you need to access private S3/secrets
# 8. Environment variables:
#    - Name: API_BASE_URL
#    - Value: https://api.arke.institute
# 9. Create
```

**5. Submit job**

```bash
# Using AWS Console:
# 1. Go to AWS Batch → Jobs → Submit new job
# 2. Job name: nara-import-full-collection
# 3. Job definition: nara-import
# 4. Job queue: (select your queue)
# 5. Submit

# Or via CLI:
aws batch submit-job \
  --job-name nara-import-full-$(date +%Y%m%d-%H%M%S) \
  --job-queue your-job-queue-name \
  --job-definition nara-import
```

**6. Monitor job**

```bash
# View logs in CloudWatch
# Go to CloudWatch → Log groups → /aws/batch/job

# Or use CLI to tail logs
aws logs tail /aws/batch/job --follow
```

**When complete**: Job status changes to `SUCCEEDED`, container auto-terminates.

**Cost estimate**: ~$0.12 for 8 hours (Fargate Spot, 1 vCPU, 2GB)

---

### Option 2: ECS Fargate (Simplest Container Option)

**Best for**: Quick containerized deployment without managing Batch

#### Setup Steps

**1. Push image to ECR** (same as Batch option above)

**2. Create ECS cluster**

```bash
aws ecs create-cluster --cluster-name nara-import-cluster --region us-east-1
```

**3. Create CloudWatch log group**

```bash
aws logs create-log-group --log-group-name /ecs/nara-import
```

**4. Register task definition**

```bash
cat > task-definition.json <<EOF
{
  "family": "nara-import",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "nara-import",
      "image": "<YOUR_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/nara-import:latest",
      "essential": true,
      "environment": [
        {
          "name": "API_BASE_URL",
          "value": "https://api.arke.institute"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nara-import",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "import"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json
```

**5. Run task**

```bash
aws ecs run-task \
  --cluster nara-import-cluster \
  --task-definition nara-import \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-xxxxx],
    securityGroups=[sg-xxxxx],
    assignPublicIp=ENABLED
  }"

# Note: Replace subnet-xxxxx and sg-xxxxx with your VPC subnet and security group
# Security group just needs outbound internet access (default works)
```

**6. Monitor task**

```bash
# View task status
aws ecs list-tasks --cluster nara-import-cluster

# View logs
aws logs tail /ecs/nara-import --follow
```

**When complete**: Task automatically stops (status: `STOPPED`, exit code: 0)

**Cost estimate**: ~$0.40 for 8 hours (Fargate on-demand, 1 vCPU, 2GB)

---

### Option 3: EC2 Spot Instance (Cheapest & Quickest)

**Best for**: Rapid deployment, lowest cost, minimal setup

#### Option A: Fully Automated (User Data Script)

**1. Launch spot instance with auto-shutdown**

```bash
# Create user-data script that runs import and shuts down
cat > user-data.sh <<'EOF'
#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

echo "Installing dependencies..."
apt-get update
apt-get install -y python3-pip awscli git

echo "Cloning repository..."
cd /opt
git clone https://github.com/YOUR_USERNAME/nara_pilot_ingest_v0.git
cd nara_pilot_ingest_v0/scripts/nara_import

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Starting NARA import..."
python3 import_full_collection.py

echo "Import complete! Shutting down instance..."
shutdown -h now
EOF

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name your-key-pair \
  --instance-market-options '{"MarketType":"spot","SpotOptions":{"SpotInstanceType":"one-time"}}' \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nara-import}]' \
  --region us-east-1

# Monitor via SSH
ssh -i your-key.pem ubuntu@<instance-ip>
tail -f /var/log/user-data.log
```

**When complete**: Instance automatically shuts down and terminates.

**Cost estimate**: ~$0.04 for 8 hours (t3.small spot)

#### Option B: Manual SSH Method

**1. Launch spot instance**

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name your-key-pair \
  --instance-market-options '{"MarketType":"spot"}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nara-import}]'
```

**2. SSH and run manually**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<instance-ip>

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip awscli git

# Clone repo (or scp files)
git clone https://github.com/YOUR_USERNAME/nara_pilot_ingest_v0.git
cd nara_pilot_ingest_v0/scripts/nara_import

# Install Python deps
pip3 install -r requirements.txt

# Run in tmux (survives SSH disconnects)
tmux
python3 import_full_collection.py

# Detach from tmux: Ctrl+B, then D
# Reattach later: tmux attach
```

**3. Terminate instance when done**

```bash
# From your local machine
aws ec2 terminate-instances --instance-ids i-xxxxx
```

**Cost estimate**: ~$0.04 for 8 hours (t3.small spot)

---

## Quick Comparison

| Option | Setup Time | Cost (8hr) | Auto-Shutdown | Best For |
|--------|-----------|-----------|---------------|----------|
| **AWS Batch** | 15-30 min | $0.12 | ✅ Yes | Production, repeated runs |
| **ECS Fargate** | 10-20 min | $0.40 | ✅ Yes | Quick containerized deploy |
| **EC2 Spot (auto)** | 5-10 min | $0.04 | ✅ Yes | Lowest cost, one-off job |
| **EC2 Spot (manual)** | 5 min | $0.04 | ❌ Manual | Quickest to start |

**My recommendation**:
- **First time**: Use **EC2 Spot (manual)** to get started quickly
- **Production**: Use **AWS Batch** for best management and auto-shutdown

---

## Environment Variables

All scripts support environment variable configuration:

```bash
# Production API (default)
export API_BASE_URL=https://api.arke.institute

# Or override for local testing
export API_BASE_URL=http://localhost:8787
```

Scripts will use `API_BASE_URL` env var if set, otherwise default to production API.

---

## Testing Before Full Import

**Test with sample data first** to verify connectivity:

```bash
# Run 3-record test
python3 test_import_sample.py

# Or limited import (300 file units)
python3 import_limited.py
```

Both scripts will:
1. Verify API connectivity to `https://api.arke.institute`
2. Download sample records from NARA S3
3. Test the complete import pipeline
4. Exit cleanly when done

---

## Monitoring and Logs

### CloudWatch Logs (Batch/ECS)

```bash
# Tail logs in real-time
aws logs tail /aws/batch/job --follow

# Or for ECS
aws logs tail /ecs/nara-import --follow
```

### EC2 Instance Logs

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<instance-ip>

# View log file
tail -f import_full_*.log

# Or user-data logs (for auto-shutdown setup)
tail -f /var/log/user-data.log
```

### Log Contents

Each import creates a timestamped log file with:
- Progress: `[123/2053] Importing: Clinton - Address on Haiti (naId:23902919, 13 objects)`
- Checkpoints: `Checkpoint: 120 records processed, 0.15 records/sec`
- Errors: Full stack traces for debugging
- Summary: Final statistics when complete

---

## Checkpoint System

The import automatically saves progress every 10 records:

```json
{
  "file_number": 15,
  "record_index": 234,
  "timestamp": "2025-10-19T14:32:18",
  "nara_to_pi": { "7585787": "01JBBQR...", ... },
  "institution_pi": "01JBBQP..."
}
```

**If job is interrupted:**
1. Checkpoint file persists
2. Just re-run the script
3. Import resumes from last checkpoint
4. No duplicate entities created (tracks NARA ID → PI mappings)

**For Docker deployments**: Mount checkpoint as volume:
```bash
-v $(pwd)/import_checkpoint.json:/app/import_checkpoint.json
```

**When complete**: Checkpoint file is automatically deleted.

---

## Auto-Shutdown Behavior

The script **already auto-exits** when the import completes:

```python
if __name__ == "__main__":
    main()  # Completes and exits
```

This means:
- ✅ **Docker containers** stop automatically (exit code 0)
- ✅ **AWS Batch jobs** mark as `SUCCEEDED` and terminate
- ✅ **ECS tasks** stop automatically
- ✅ **EC2 user-data script** triggers `shutdown -h now`

**No code changes needed!** The script is batch-job ready.

---

## Cost Estimates (Full Import, 8 hours)

| Service | Instance | Spot? | Total Cost |
|---------|----------|-------|------------|
| AWS Batch | 1 vCPU, 2GB Fargate | Yes | **$0.12** |
| AWS Batch | 1 vCPU, 2GB Fargate | No | $0.40 |
| ECS Fargate | 1 vCPU, 2GB | No | $0.40 |
| EC2 | t3.small | Yes | **$0.04** |
| EC2 | t3.small | No | $0.17 |

**Note**: Prices approximate for us-east-1 region. Actual costs may vary.

---

## Network Requirements

### Outbound Access Required

Your AWS environment needs outbound HTTPS access to:
- `https://api.arke.institute` - Arke IPFS API
- `https://nara-national-archives-catalog.s3.amazonaws.com` - NARA S3 bucket (via AWS CLI)

### Security Group Rules

For ECS/Batch, create security group with:
- **Outbound**: Allow HTTPS (443) to `0.0.0.0/0`
- **Inbound**: None needed (batch job, not a service)

### No VPN/VPC Peering Needed

Since the API is publicly accessible at `https://api.arke.institute`, you don't need:
- ❌ VPC peering
- ❌ VPN connections
- ❌ Private link
- ❌ NAT gateway configuration (if using public subnet)

**Just enable "Assign Public IP"** when launching ECS/Batch tasks.

---

## Troubleshooting

### "Connection refused" or API timeout

**Check API is accessible:**
```bash
curl https://api.arke.institute
# Expected: {"service":"arke-ipfs-api","version":"0.1.0","status":"ok"}
```

**Verify outbound access** from your AWS environment:
```bash
# From EC2/container
curl -v https://api.arke.institute
```

### Script exits immediately

**Check logs** for errors:
- CloudWatch: `/aws/batch/job` or `/ecs/nara-import`
- EC2: `import_full_*.log`

**Common causes**:
- API unreachable (check network/security group)
- Missing dependencies (verify `pip install -r requirements.txt` succeeded)
- Invalid checkpoint file (delete and restart)

### S3 download failures

**NARA S3 bucket is public**, no credentials needed:
```bash
# Test download
aws s3 cp s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-1.jsonl - --no-sign-request
```

**If downloads fail**:
- Verify AWS CLI is installed: `aws --version`
- Check outbound access to S3

### Out of memory

Unlikely (script uses <1GB), but if it happens:
- Increase memory allocation to 4GB
- Check for runaway processes

### Checkpoint not persisting (Docker)

**For local Docker**:
```bash
docker run -v $(pwd)/import_checkpoint.json:/app/import_checkpoint.json ...
```

**For ECS/Batch**: Use EFS volume or don't worry about it (job completes in one run)

---

## Local Testing

**Before deploying to AWS**, test locally:

### Option 1: Direct Python

```bash
cd scripts/nara_import
pip install -r requirements.txt

# Test with 3 records (quick)
python3 test_import_sample.py

# Limited import (300 file units, ~30 min)
python3 import_limited.py

# Full import (2,053 file units, 4-8 hours)
python3 import_full_collection.py
```

### Option 2: Docker

```bash
cd scripts/nara_import

# Build
docker build -t nara-import .

# Run test import
docker run --rm nara-import python test_import_sample.py

# Run full import
docker run --rm \
  -v $(pwd)/import_checkpoint.json:/app/import_checkpoint.json \
  nara-import

# Or use docker-compose
docker-compose up
```

---

## Quick Start: EC2 Spot (Fastest Path)

**Get started in 5 minutes:**

```bash
# 1. Launch spot instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name YOUR_KEY_NAME \
  --instance-market-options '{"MarketType":"spot"}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nara-import}]'

# 2. Get instance IP
aws ec2 describe-instances --filters "Name=tag:Name,Values=nara-import" \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

# 3. SSH in
ssh -i your-key.pem ubuntu@<IP>

# 4. Run import
git clone https://github.com/YOUR_USERNAME/nara_pilot_ingest_v0.git
cd nara_pilot_ingest_v0/scripts/nara_import
pip3 install -r requirements.txt
python3 test_import_sample.py  # Start with test!

# 5. If test succeeds, run full import
tmux
python3 import_full_collection.py
# Ctrl+B, D to detach

# 6. When done, terminate instance
exit
aws ec2 terminate-instances --instance-ids i-xxxxx
```

**Total cost**: ~$0.04 for 8-hour import

---

## Next Steps

1. **Choose your deployment option** based on needs:
   - Need automation? → **AWS Batch**
   - Want containers? → **ECS Fargate**
   - Want cheap & fast? → **EC2 Spot**

2. **Test first** with `test_import_sample.py` (3 records, 1 minute)

3. **Deploy and monitor** logs for first run

4. **Checkpoint system** handles interruptions automatically

5. **Script auto-exits** when complete - no manual cleanup needed!

Need help with a specific deployment option? Let me know!
