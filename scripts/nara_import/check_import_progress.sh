#!/bin/bash
# Check import progress

LOGDIR="/Users/chim/Working/arke_institute/nara_pilot_ingest_v0/scripts/nara_import"

echo "========================================="
echo "NARA Import Progress Check"
echo "========================================="
echo ""

# Check if process is running
PID=$(ps aux | grep import_full_collection | grep -v grep | awk '{print $2}')
if [ -z "$PID" ]; then
    echo "⚠️  Import process NOT running"
else
    echo "✅ Import process running (PID: $PID)"
fi
echo ""

# Check checkpoint
if [ -f "$LOGDIR/import_checkpoint.json" ]; then
    echo "📍 Checkpoint:"
    cat "$LOGDIR/import_checkpoint.json" | python3 -m json.tool
    echo ""
fi

# Find latest log file
LATEST_LOG=$(ls -t "$LOGDIR"/import_full_*.log 2>/dev/null | head -1)

if [ -n "$LATEST_LOG" ]; then
    echo "📝 Latest log: $(basename $LATEST_LOG)"
    echo "   Size: $(ls -lh "$LATEST_LOG" | awk '{print $5}')"
    echo ""

    # Count records processed
    RECORDS=$(grep -c "Importing:" "$LATEST_LOG" 2>/dev/null || echo 0)
    echo "📊 Records processed: $RECORDS"

    # Count digital objects created
    OBJECTS=$(grep -c "Created digital object" "$LATEST_LOG" 2>/dev/null || echo 0)
    echo "   Digital objects created: $OBJECTS"
    echo ""

    # Show last 10 lines
    echo "📄 Last 10 log lines:"
    tail -10 "$LATEST_LOG"
fi

echo ""
echo "========================================="
echo "Run this script periodically to check progress"
echo "Full import estimated time: 4-8 hours"
echo "========================================="
