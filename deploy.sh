#!/bin/bash
# PolyBot Deployment Script

echo "============================================="
echo "🚀 Deploying PolyBot..."
echo "============================================="

# Ensure we are in the bot directory
cd "$(dirname "$0")"

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment '.venv' not found. Please set one up first."
    exit 1
fi

# Stop any existing running bot instance using pkill
echo "Stopping any existing PolyBot instances..."
pkill -f "python main.py"
sleep 2

# Check if DRY_RUN is active
if grep -q 'DRY_RUN="True"' .env; then
    echo "⚠️  WARNING: PolyBot is running in DRY_RUN mode."
    echo "Orders will be simulated but NOT traded on Polymarket."
else
    echo "🔥 DANGER: PolyBot is running LIVE with real capital."
fi

# Start the bot in the background using nohup
echo "Starting main.py in the background..."
nohup python main.py > polybot.log 2>&1 &
echo "✅ PolyBot successfully started! Streaming live logs now (Press Ctrl+C to exit log view, the bot will keep running):"
echo ""

# Stream the logs to the terminal, filtering for PNL and execution notices
tail -f polybot.log | grep -E --line-buffered "PNL|PROFIT|LOSS|WATER MARK|MILESTONE|Sweep"
