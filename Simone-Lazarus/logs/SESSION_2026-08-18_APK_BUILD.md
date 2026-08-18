## SESSION 2026-08-18 — APK v2 REBUILD (STANDALONE)

### Problem
v1 APK depended on Termux/Python bridge — failed on device without Termux.
Bridge couldn't start (no python3 on Android), API endpoint was wrong.

### Changes
- Removed all bridge/Termux dependency from APK
- Gemini API called directly from Kotlin (no Python middleman)
- OpenRouter fallback for non-Gemini keys
- Native Android tools: SMS, calls, camera, GPS, contacts, call log, battery, storage, BT scan, shell
- WebView UI with tool grid buttons + chat
- API key saved in SharedPreferences (survives restart)
- Auto-speak replies toggle
- System prompt baked in
- Wake lock for 12 hours
- Version bump to 2.0.0

### Build
- Kotlin errors fixed: MediaStore import, BATTERY_PROPERTY_TEMPERATURE → IntentFilter
- Built successfully, signed with jarsigner (v1 scheme)
- Size: 4.6MB

### Delivery
- Catbox: https://files.catbox.moe/wdh9j4.apk
- Local: ~/Desktop/BruceClaw-v2.apk

### Key difference from v1
v1 = APK shell that required Termux + Python bridge running separately
v2 = Fully self-contained, just add Gemini API key and chat
