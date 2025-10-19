#!/bin/bash
# EC2 User Data Script - Full Import with Auto-Shutdown
# Runs import_full_collection.py (2,053 file units, 4-8 hours) then shuts down

set -e
exec > >(tee /var/log/nara-import.log) 2>&1

echo "========================================="
echo "NARA Import - FULL COLLECTION MODE"
echo "Starting at: $(date)"
echo "Expected runtime: 4-8 hours"
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

# Run FULL import
echo "[5/5] Running FULL import (2,053 file units)..."
echo "========================================="
START_TIME=$(date +%s)

python3 import_full_collection.py

# Check exit code
EXIT_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(((DURATION % 3600) / 60))

if [ $EXIT_CODE -eq 0 ]; then
    echo "========================================="
    echo "✓ FULL IMPORT COMPLETED SUCCESSFULLY"
    echo "Completed at: $(date)"
    echo "Total runtime: ${HOURS}h ${MINUTES}m"
    echo "========================================="
    
    echo ""
    echo "Auto-shutdown in 60 seconds..."
    sleep 60
    
    shutdown -h now
else
    echo "✗ FULL IMPORT FAILED (exit code: $EXIT_CODE)"
    echo "Instance will remain running for debugging"
    echo "Check logs:"
    echo "  - /var/log/nara-import.log"
    echo "  - $(ls -t import_full_*.log 2>/dev/null | head -1)"
fi
