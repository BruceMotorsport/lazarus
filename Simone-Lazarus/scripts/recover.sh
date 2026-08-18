#!/bin/bash
# Simone Lazarus Recovery Script
# Run this when I crash to restore everything

echo "=== Simone Lazarus Recovery ==="
echo "Restoring from backup..."

# Create directories
mkdir -p ~/.openclaw/workspace
mkdir -p ~/bruceclaw_messages

# Copy tools
cp ~/Desktop/Simone-Lazarus/tools/bridge_final.py ~/bridge.py
cp ~/Desktop/Simone-Lazarus/tools/tools.json ~/tools.json
cp ~/Desktop/Simone-Lazarus/tools/TOOLS.md ~/.openclaw/workspace/TOOLS.md

# Copy configs
cp ~/Desktop/Simone-Lazarus/configs/knowledge_base.json ~/knowledge_base.json

# Start bridge
pkill -f bridge 2>/dev/null
sleep 1
termux-wake-lock
python3 ~/bridge.py &

echo "Recovery complete!"
echo "Bridge should be running on port 9999"
echo "Check: curl -s http://localhost:9999/"
