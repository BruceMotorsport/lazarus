#!/bin/bash
echo "Cleaning Termux..."
rm -rf ~/nexus.py ~/bridge.py ~/keepalive.py ~/openclaw ~/.openclaw ~/Lazarus
echo "Installing Lazarus..."
curl -sL https://raw.githubusercontent.com/BruceMotorsport/lazarus/main/core/lazarus.py -o ~/Lazarus_core.py
mkdir -p ~/Lazarus/{memory,tools,config,logs,mcp,skills}
curl -sL https://raw.githubusercontent.com/BruceMotorsport/lazarus/main/config/CONSTITUTION.md -o ~/Lazarus/config/CONSTITUTION.md
curl -sL https://raw.githubusercontent.com/BruceMotorsport/lazarus/main/config/settings.json -o ~/Lazarus/config/settings.json
echo "Done! Type 'python3 ~/Lazarus_core.py' to start."
