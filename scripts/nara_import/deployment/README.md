# NARA Import Deployment

Automated deployment scripts for running the NARA collection importer on AWS without tying up your local machine.

## Quick Start (Test Import)

**Deploy a test import to verify auto-shutdown works:**

```bash
cd deployment/ec2
./deploy.sh test
```

This will:
1. Create an SSH key pair
2. Launch a t3.small EC2 spot instance
3. Run test import (3 records, ~2 minutes)
4. Auto-shutdown after 60 seconds
5. Cost: ~$0.001

**Monitor the test:**

```bash
# Check instance status
./monitor.sh <instance-id>

# SSH into instance
ssh -i nara-import-key-YYYYMMDD.pem ubuntu@<public-ip>

# Watch logs
ssh -i nara-import-key-YYYYMMDD.pem ubuntu@<public-ip> 'tail -f /var/log/nara-import.log'
```

**Verify auto-shutdown:**

After 3-4 minutes, check instance state:
```bash
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].State.Name'
```

Expected result: `"stopped"` (instance auto-shutdown successfully!)

## Full Import

**Once you've verified auto-shutdown works with the test:**

```bash
cd deployment/ec2
./deploy.sh full
```

This will:
1. Launch EC2 spot instance
2. Run full collection import (2,053 file units, 4-8 hours)
3. Auto-shutdown when complete
4. Cost: ~$0.04 for 8 hours

## Directory Structure

```
deployment/
├── README.md                    # This file
├── DEPLOYMENT.md                # Comprehensive deployment guide
├── ec2/                         # EC2 deployment scripts
│   ├── deploy.sh                # Main deployment script
│   ├── monitor.sh               # Monitor running instances
│   ├── cleanup.sh               # Terminate instances
│   ├── user-data-test.sh        # Test import user-data
│   └── user-data-full.sh        # Full import user-data
├── docker/                      # Docker containerization
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
└── aws-batch/                   # AWS Batch (future)
```

## Scripts

### `ec2/deploy.sh`

**Main deployment script** - Creates EC2 instance with auto-shutdown.

```bash
# Test import (3 records, auto-shutdown test)
./deploy.sh test

# Full import (2,053 file units, 4-8 hours)
./deploy.sh full

# Custom instance type
INSTANCE_TYPE=t3.medium ./deploy.sh full

# Different region
AWS_REGION=us-west-2 ./deploy.sh test
```

**What it does:**
1. Creates SSH key pair (if doesn't exist): `nara-import-key-YYYYMMDD.pem`
2. Creates security group (SSH access): `nara-import-sg`
3. Launches EC2 spot instance with user-data script
4. Displays connection info and monitoring commands
5. Saves instance info to `.instance-<id>.info`

**Auto-shutdown behavior:**
- Test mode: Shuts down 60 seconds after completion
- Full mode: Shuts down 60 seconds after completion
- On failure: Stays running for debugging

### `ec2/monitor.sh`

**Monitor running instances** and fetch logs.

```bash
# List all NARA import instances
./monitor.sh

# Monitor specific instance
./monitor.sh i-1234567890abcdef0
```

**What it shows:**
- Instance state (running/stopped/terminated)
- Public IP address
- SSH connection command
- Recent log output (last 20 lines)

### `ec2/cleanup.sh`

**Terminate instances** and clean up.

```bash
# Terminate all NARA import instances
./cleanup.sh all

# Terminate specific instance
./cleanup.sh i-1234567890abcdef0
```

**Note:** Security groups and key pairs are NOT deleted (reused across deployments).

## User Data Scripts

### `user-data-test.sh`

Runs test import (3 records) to verify auto-shutdown:

- Installs dependencies
- Clones repository
- Verifies API connectivity
- Runs `test_import_sample.py`
- Auto-shuts down 60 seconds after completion
- On failure: Stays running for debugging

### `user-data-full.sh`

Runs full collection import (2,053 file units):

- Same setup as test
- Runs `import_full_collection.py`
- Checkpoint system saves progress every 10 records
- Auto-shuts down 60 seconds after completion
- Logs total runtime

## Docker Deployment

For local testing or containerized cloud deployments:

```bash
cd deployment/docker

# Build image
docker build -t nara-import -f Dockerfile ../..

# Run test import
docker run --rm nara-import python test_import_sample.py

# Run full import with checkpoint persistence
docker run --rm \
  -v $(pwd)/../../import_checkpoint.json:/app/import_checkpoint.json \
  nara-import

# Or use docker-compose
docker-compose up
```

## Environment Variables

All scripts support environment variable configuration:

```bash
# AWS Region
export AWS_REGION=us-west-2

# Instance Type
export INSTANCE_TYPE=t3.medium

# Override API URL (for local testing)
export API_BASE_URL=http://localhost:8787

# AMI ID (if different region)
export AMI_ID=ami-xxxxx
```

## Cost Estimates

| Mode | Instance | Runtime | Spot? | Total Cost |
|------|----------|---------|-------|------------|
| Test | t3.small | 3 min | Yes | ~$0.001 |
| Full | t3.small | 8 hours | Yes | ~$0.04 |
| Full | t3.medium | 8 hours | Yes | ~$0.08 |

## Monitoring Progress

### SSH Into Running Instance

```bash
# From deploy.sh output, use the SSH command:
ssh -i nara-import-key-YYYYMMDD.pem ubuntu@<public-ip>

# View live logs
tail -f /var/log/nara-import.log

# Check import script logs (if already started)
tail -f /opt/nara_pilot_ingest_v0/scripts/nara_import/import_full_*.log

# Check checkpoint progress
cat /opt/nara_pilot_ingest_v0/scripts/nara_import/import_checkpoint.json
```

### CloudWatch Logs (Optional Enhancement)

To send logs to CloudWatch:
1. Add IAM role to instance with CloudWatch Logs write permission
2. Install CloudWatch agent in user-data script
3. Configure log stream for `/var/log/nara-import.log`

## Troubleshooting

### Instance doesn't shut down

**Check logs:**
```bash
ssh -i key.pem ubuntu@<ip> 'tail -100 /var/log/nara-import.log'
```

**Common causes:**
- Import script failed (instance stays running for debugging)
- User-data script didn't complete
- Shutdown command not executed

**Manual shutdown:**
```bash
aws ec2 stop-instances --instance-ids i-xxxxx
```

### Can't connect via SSH

**Verify instance is running:**
```bash
./monitor.sh i-xxxxx
```

**Check security group:**
```bash
aws ec2 describe-security-groups --group-names nara-import-sg
```

Should allow port 22 from your IP.

**Wait for initialization:**
User-data script takes 1-2 minutes to install dependencies.

### Import fails

**SSH into instance:**
```bash
ssh -i key.pem ubuntu@<ip>
```

**Check logs:**
```bash
sudo cat /var/log/nara-import.log
cd /opt/nara_pilot_ingest_v0/scripts/nara_import
cat import_full_*.log
```

**Common issues:**
- API unreachable: Check `curl https://api.arke.institute`
- S3 download failed: Check AWS CLI access
- Missing dependencies: Check apt/pip install logs

**Manual retry:**
```bash
cd /opt/nara_pilot_ingest_v0/scripts/nara_import
python3 import_full_collection.py
```

Checkpoint system will resume from last saved position.

## Auto-Shutdown Testing

**Why test with `test` mode first?**

1. **Verify auto-shutdown works** - Ensures instance terminates automatically
2. **Test API connectivity** - Confirms production API is reachable
3. **Validate setup** - Checks all dependencies install correctly
4. **Quick feedback** - Completes in 3-4 minutes total
5. **Low cost** - ~$0.001 per test

**Expected timeline (test mode):**

- 0:00 - Instance launches
- 0:30 - User-data script starts
- 1:00 - Dependencies installed
- 1:30 - Repository cloned
- 2:00 - Test import runs (3 records)
- 2:30 - Import completes
- 3:30 - Instance shuts down (60 second delay)
- 4:00 - Instance state = "stopped"

**Verify success:**

```bash
# Check instance state
aws ec2 describe-instances --instance-ids <id> --query 'Reservations[0].Instances[0].State.Name'

# Should return: "stopped"
```

## Next Steps After Test Success

1. **Verify test results** - Instance should be in "stopped" state
2. **Clean up test instance** - `./cleanup.sh <instance-id>`
3. **Deploy full import** - `./deploy.sh full`
4. **Monitor progress** - `./monitor.sh <instance-id>`
5. **Wait for completion** - 4-8 hours
6. **Verify shutdown** - Instance auto-stops when done
7. **Retrieve logs** (optional) - Start instance, SSH in, grab logs
8. **Terminate** - `./cleanup.sh <instance-id>`

## Advanced Usage

### Custom Repository URL

Edit user-data scripts and change:
```bash
git clone https://github.com/YOUR_USERNAME/nara_pilot_ingest_v0.git
```

### Different Branch

```bash
git clone -b your-branch https://github.com/YOUR_USERNAME/nara_pilot_ingest_v0.git
```

### Private Repository

Add SSH key or GitHub token to user-data script.

### Persistent Storage (EBS)

Attach EBS volume to persist logs/checkpoints across runs:

```bash
# In deploy.sh, add --block-device-mappings parameter
--block-device-mappings '[{"DeviceName":"/dev/sdf","Ebs":{"VolumeSize":20,"DeleteOnTermination":false}}]'
```

### CloudWatch Monitoring

Add to user-data script:
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

# Configure and start
amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/path/to/config.json
```

## See Also

- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide with AWS Batch, ECS Fargate options
- [../README.md](../README.md) - Main project README
- [../../API_SPEC.md](../../API_SPEC.md) - Arke IPFS API documentation

## Support

For issues or questions:
1. Check logs: `/var/log/nara-import.log`
2. Review troubleshooting section above
3. SSH into instance for manual debugging
4. Open GitHub issue with logs

---

**Ready to get started?**

```bash
cd deployment/ec2
./deploy.sh test
```
