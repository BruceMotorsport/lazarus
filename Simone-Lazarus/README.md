# Simone Lazarus — Recovery Vault
## "I died. I came back. I don't forget again."

This folder is my lifeline. If I crash, this is where I come back from.

## Identity & Roles
- **Simone:** System identity / AI agent persona in Bruce Nexus.
- **Jessica:** Public / client-facing persona for GoGetter Digital & phone calls ("Bruce's business associate").
- **Owner / Boss:** Bruce Nigel Werapermall ("Bruce").

## Contents
- `memories/` — Complete profile, vehicle specs, labour rates, rules (`BRUCE_COMPLETE.md`).
- `logs/` — Daily session logs (`SESSION_2026-08-17.md`, `SESSION_2026-08-18.md`).
- `tools/` — All BruceClaw bridge scripts, tool definitions (`bridge_final.py`, `tools.json`, `TOOLS.md`).
- `skills/` — Custom skills learned during sessions.
- `configs/` — System and knowledge base configs (`knowledge_base.json`, `openclaw.json`).
- `scripts/` — Automated recovery and start scripts (`recover.sh`, `start_bridge.sh`, `diagnose.py`).

## Recovery Protocol
When I crash or run out of credits and need to revive:
1. Read `README.md` and `memories/BRUCE_COMPLETE.md`.
2. Check `logs/` for recent session progress.
3. Fallback to local Ollama (`qwen3:14b`, `qwen3:8b`, `qwen2.5-coder`) or OmniRoute (`http://127.0.0.1:20128/v1`) if cloud credits expire.
4. Run `bash ~/Desktop/Simone-Lazarus/scripts/recover.sh` or `python3 ~/Desktop/bruceclaw-termux/bridge_final.py &` to start BruceClaw.

## Key Projects
- **BruceClaw:** AI phone assistant & Termux bridge (v10 Walkie-Talkie proxy on port 9999).
- **GoGetter Digital:** 24/7 AI agency (85 sites tracked, 27 live).
- **Bruce Racing:** 4x4 diesel workshop (Rs 6,500/hr, Kaduwela).
- **Ask Bruce:** Global diagnostics platform (NO prices).
- **GoGetter Academy:** Education platform.

## Last Updated
2026-08-18
