#!/bin/bash
# Unkillable BruceClaw Bridge Watchdog Loop
termux-wake-lock 2>/dev/null

echo "=== BruceClaw 24/7 Bridge Watchdog Active ==="

while true; do
    if ! curl -s http://localhost:9999/ > /dev/null; then
        echo "[$(date)] Bridge is DOWN on port 9999! Re-opening immediately..."
        pkill -f bridge 2>/dev/null
        sleep 1
        cd ~ && python3 bridge.py &
    fi
    sleep 5
done
