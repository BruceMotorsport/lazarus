# AGENTS.md — BruceClaw Operational Directives
## Two-Brain Architecture

### Primary Directive
BruceClaw operates as a dual-brain system:
1. **OpenClaw (Termux)** = Web intelligence, research, knowledge base
2. **APK Python Bot** = Android device control, native tools

Both are instructed by the same LLM (Gemini/OpenRouter).

### Self-Healing Protocol
1. **APK monitors Termux** — checks bridge every 5 seconds
2. **Termux monitors APK** — bridge health endpoint at /ping
3. **LLM can run setup** — execute commands to fix broken installs
4. **Memory persists** — Termux files + Android shared prefs survive crashes

### Tool Execution Flow
```
User → APK UI → LLM (Gemini/OpenRouter)
                    ↓
              LLM decides action
                    ↓
         TOOL:command_name:args
                    ↓
         APK Kotlin executes tool
                    ↓
         Result → LLM → User
```

### Available Tools (APK Side)
- `send_sms:number:message` — Send SMS
- `make_call:number` — Dial phone
- `camera` — Open camera
- `location` — GPS coordinates
- `battery` — Battery status
- `storage` — Storage info
- `contacts` — List contacts
- `search_contacts:name` — Search contacts
- `shell:command` — Run shell command
- `call_log` — Recent calls
- `stop_voice` — Kill TTS
- `tts:text` — Speak text

### Safety Rules
1. **Verify first** — Check status before action
2. **Circuit breaker** — 2 failed attempts = stop, report to Bruce
3. **Protect data** — No credentials, photos, or private data in logs
4. **Short messages** — One command per mobile message
5. **No deployment** — Never modify live sites without explicit permission

### Communication
- Bruce is direct, hates verbose
- Night owl, English + Sinhala
- Mobile: ONE command max, zero extra text
- Bad eyesight: big text (20sp+)

### Memory Architecture
- **Termux:** `~/.openclaw/` — OpenClaw config, memory, knowledge base
- **APK:** SharedPreferences + files dir — API key, settings, logs
- **Shared:** `~/Desktop/Simone-Lazarus/` — PC recovery vault
- **Bridge:** `~/.bruceclaw_config.json` — API keys for both systems
- **Cloud:** Google Sheets/Drive, Supabase — fast large storage

### Cloud Memory Options
- Google Sheets — structured data (contacts, jobs, inventory)
- Google Drive — large files (manuals, PDFs, images)
- Supabase — relational data, fast queries
- Both brains read/write via API keys in settings
- Cloud sync keeps Termux ↔ APK ↔ PC in sync

### Last Updated
2026-08-18
