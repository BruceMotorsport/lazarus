#!/bin/bash
# Start BruceClaw Bridge with 24/7 Watchdog
termux-wake-lock 2>/dev/null

pkill -f bridge 2>/dev/null
sleep 1
cd ~ && python3 bridge.py &

echo "BruceClaw Bridge started on port 9999!"
echo "Starting watchdog loop..."
bash ~/Desktop/bruceclaw-termux/keep_termux_alive.sh &
