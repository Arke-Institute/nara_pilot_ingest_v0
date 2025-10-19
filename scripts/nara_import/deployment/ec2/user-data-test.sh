#!/bin/bash
# EC2 User Data Script - Test Import with Auto-Shutdown
# Runs test_import_sample.py (3 records) then shuts down to verify auto-shutdown works

set -e
exec > >(tee /var/log/nara-import.log) 2>&1

echo "========================================="
echo "NARA Import - TEST MODE"
echo "Starting at: $(date)"
echo "========================================="

# Install dependencies
echo "[1/5] Installing dependencies..."
apt-get update -qq
apt-get install -y -qq python3-pip awscli git tmux

# Clone repository
echo "[2/5] Cloning repository..."
cd /opt
if [ ! -d "nara_pilot_ingest_v0" ]; then
    git clone https://github.com/Arke-Institute/nara_pilot_ingest_v0.git
fi
cd nara_pilot_ingest_v0/scripts/nara_import

# Install Python dependencies
echo "[3/5] Installing Python dependencies..."
pip3 install -q -r requirements.txt

# Verify API connectivity
echo "[4/5] Verifying API connectivity..."
if curl -s --max-time 10 https://api.arke.institute > /dev/null; then
    echo "✓ API is reachable"
else
    echo "✗ API is not reachable!"
    exit 1
fi

# Run TEST import (3 records, ~1 minute)
echo "[5/5] Running TEST import (3 records)..."
echo "========================================="
python3 test_import_sample.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "========================================="
    echo "✓ TEST IMPORT COMPLETED SUCCESSFULLY"
    echo "Completed at: $(date)"
    echo "========================================="
    
    echo ""
    echo "Auto-shutdown in 60 seconds..."
    echo "SSH into instance to cancel: sudo shutdown -c"
    sleep 60
    
    shutdown -h now
else
    echo "✗ TEST IMPORT FAILED"
    echo "Instance will remain running for debugging"
    echo "Check logs: /var/log/nara-import.log"
fi
