# Quick Start - Deploy NARA Import to AWS

## Step 1: Test Auto-Shutdown (3 minutes)

First, verify auto-shutdown works with a quick test:

```bash
cd deployment/ec2
./deploy.sh test
```

**What happens:**
- Creates EC2 spot instance (~$0.001)
- Imports 3 test records (2 minutes)
- Auto-shuts down instance (60 seconds later)
- **Total time: ~3-4 minutes**

**Monitor the test:**
```bash
# Copy instance-id from deploy.sh output
./monitor.sh <instance-id>

# Or watch logs live
ssh -i nara-import-key-*.pem ubuntu@<public-ip> 'tail -f /var/log/nara-import.log'
```

**Verify auto-shutdown worked:**
```bash
# After 4 minutes, check instance state
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].State.Name'

# Should return: "stopped" ✓
```

## Step 2: Run Full Import (4-8 hours)

Once test succeeds, deploy full import:

```bash
cd deployment/ec2
./deploy.sh full
```

**What happens:**
- Creates EC2 spot instance (~$0.04 for 8 hours)
- Imports 2,053 file units with 45,936 digital objects
- Saves checkpoint every 10 records
- Auto-shuts down when complete
- **Total time: 4-8 hours**

**Monitor progress:**
```bash
./monitor.sh <instance-id>
```

**Check status:**
```bash
# Instance state
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].State.Name'

# When "stopped" = import complete! ✓
```

## Step 3: Cleanup

```bash
# Terminate instance
./cleanup.sh <instance-id>

# Or terminate all NARA import instances
./cleanup.sh all
```

## That's It!

The scripts handle everything:
- ✅ SSH key creation
- ✅ Security group setup
- ✅ EC2 instance launch
- ✅ Dependency installation
- ✅ Repository cloning
- ✅ Import execution
- ✅ Auto-shutdown

## Need Help?

- **Full documentation**: `deployment/README.md`
- **EC2 details**: `deployment/ec2/README.md`
- **Troubleshooting**: `deployment/DEPLOYMENT.md`
- **Monitor instances**: `./deployment/ec2/monitor.sh`

---

**Ready? Start with the test:**

```bash
cd deployment/ec2
./deploy.sh test
```
