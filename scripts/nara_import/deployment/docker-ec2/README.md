# Docker EC2 Deployment

Deploy NARA import to EC2 using Docker. Start import and check status whenever you want.

## Quick Start

```bash
# Test import (3 records, ~2 minutes)
./deploy.sh test

# Full import (2,053 records, 4-8 hours)
./deploy.sh full
```

## How It Works

1. **Launch EC2** - t3.small spot instance with Docker
2. **Rsync files** - Upload project (~5MB)
3. **Build Docker** - Same Dockerfile we tested locally
4. **Start container** - Run in background, exit immediately
5. **You check status** - Poll whenever you want
6. **You shutdown** - When done, shutdown instance

## New Workflow (Fire and Forget)

```bash
# 1. Deploy (takes ~4 minutes, then exits)
./deploy.sh test
# Output: "Import Started!"
#         "Instance ID: i-xxxxx"
#         "Check status: ./check.sh i-xxxxx"

# 2. Later... check status (whenever you want)
./check.sh i-xxxxx
# Shows: instance state, container status, last 50 lines of logs
# If done: "Import Complete! Shutdown? (y/n)"

# 3. Shutdown when done
./check.sh i-xxxxx --shutdown
# Or just answer 'y' when prompted
```

## Scripts

- **deploy.sh** - Launch instance, start container, exit
- **check.sh** - Check status, show logs, shutdown option
- **monitor.sh** - Continuously poll until done
- **cleanup.sh** - Terminate instance immediately
- **user-data.sh** - EC2 init (installs Docker)

## Monitoring Options

### Option 1: Poll Manually (Recommended)
Check whenever you're curious if it's done:
```bash
./check.sh i-xxxxx
```

### Option 2: Monitor Continuously
Automatically poll every 30 seconds until done:
```bash
./monitor.sh i-xxxxx

# Custom interval (60 seconds)
./monitor.sh i-xxxxx 60
```

### Option 3: View Live Logs via SSH
Get instance info, then SSH in:
```bash
# check.sh shows the SSH command
./check.sh i-xxxxx
# Then run the displayed SSH command to tail logs
```

## Timeline

### Test Mode
```
0:00  Launch instance
1:00  SSH ready
1:30  Files uploaded
2:00  Docker build starts
3:30  Docker build complete
3:30  Container starts (deploy.sh exits here)
3:32  Import completes
      (you check status whenever)
      (you shutdown when ready)
```

### Full Mode
```
0:00  Launch instance
3:30  Container starts (deploy.sh exits here)
3:30-8:00hrs  Importing 2,053 file units
      (you poll occasionally to check progress)
8:00hrs  Import completes
      (you check status and shutdown)
```

## check.sh Features

When you run `./check.sh <instance-id>`:

**If import still running:**
- Shows instance state and uptime
- Shows container status
- Shows last 50 lines of logs
- Suggests checking again later

**If import finished:**
- Shows final status (success/failure)
- Shows last 50 lines of logs
- Prompts: "Shutdown instance? (y/n)"
- Or use `--shutdown` flag to skip prompt

## Examples

```bash
# Deploy test import
./deploy.sh test
# Output: Instance ID: i-0abc123...

# Check 2 minutes later
./check.sh i-0abc123
# Shows logs, "Import still running..."

# Check again 5 minutes later
./check.sh i-0abc123
# Shows "Import Complete! Shutdown? (y/n)"

# Answer 'y' to shutdown, or:
./check.sh i-0abc123 --shutdown

# Or monitor continuously (polls every 30s)
./monitor.sh i-0abc123
# Exits automatically when import completes
```

## Cleanup

```bash
# Graceful shutdown (if import done)
./check.sh <instance-id> --shutdown

# Force terminate (anytime)
./cleanup.sh <instance-id>

# Terminate all NARA import instances
./cleanup.sh all
```

## Cost

- **Test**: ~$0.001 (5 minutes)
- **Full**: ~$0.04 (8 hours on t3.small spot)

## Why This Workflow?

- ✅ **No waiting** - Deploy script exits immediately
- ✅ **Check anytime** - Poll when you're curious
- ✅ **No always-on script** - No script running on your computer for hours
- ✅ **Easy shutdown** - Prompted when import completes
- ✅ **Flexible** - Monitor continuously or check manually

## What Gets Uploaded

```
scripts/nara_import/
├── *.py (all Python scripts)
├── lib/ (library code)
├── requirements.txt
├── deployment/docker/ (Dockerfile)
└── config/ (collection configs)
```

**Excluded**: logs, cache, git, old deployment scripts

## Troubleshooting

### "Container not found"
- Wait ~30 seconds after deploy.sh completes
- Container is still starting up

### SSH connection fails
- Wait 60 seconds for user-data to complete
- Check security group has SSH access
- Verify key file exists in ~/.ssh/

### Import fails
- check.sh will show exit code and logs
- SSH in to debug: `ssh -i ~/.ssh/nara-import-key-*.pem ubuntu@<ip>`
- View full logs: `docker logs nara-import`

### Want to re-run import
```bash
# SSH to instance
ssh -i ~/.ssh/nara-import-key-*.pem ubuntu@<ip>

# Remove old container
docker rm nara-import

# Re-run
docker run -d --name nara-import nara-import python test_import_sample.py
```

## Next Steps

1. **Test deployment**: `./deploy.sh test`
2. **Wait 4-5 minutes** (for deploy to finish)
3. **Check status**: `./check.sh <instance-id>`
4. **See import complete**
5. **Shutdown**: Answer 'y' when prompted
6. **Deploy full import**: `./deploy.sh full`

---

**Ready to deploy!** Your local computer won't be tied up for hours. Just deploy, check status whenever you want, and shutdown when done.
