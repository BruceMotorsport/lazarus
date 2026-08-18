# JESSICA — NOW.md (Current Status)

**Last updated:** 2026-08-18 22:00

## What I'm Working On
- Bruce Racing chatbot — fixed Groq model (qwen/qwen3.6-27b), removed AI Tutor fallback
- GoGetter Engine API — deployed to Vercel with working LLM
- New Lazarus file structure — building this20-point system

## What's Working
- ✅ Bruce Racing chatbot (bruce-racing-pvt.web.app/chat.html)
- ✅ GoGetter Engine API (gogetter-engine.vercel.app/api/chat)
- ✅ Vision model (opencode-zen + mimo-v2.5)
- ✅ Groq API (qwen/qwen3.6-27b)
- ✅ Firebase hosting

## What's Broken
- ❌ MIMO API (out of credits)
- ❌ xAI API (out of credits)
- ❌ GLM API (rate limited + privacy violation — BANNED)
- ❌ BruceClaw app installer (pkg/git/pip3 missing, read-only filesystem)

## Recent Fixes (Aug 18)
- Chatbot Groq model: llama-3.3-70b-versatile → qwen/qwen3.6-27b
- Chatbot fallback: removed "AI Tutor" message, now says "call 077 225 6655"
- TTS: strips markdown symbols before speaking
- System prompts: added "plain text only, no markdown"
- Vision: fixed provider to opencode-zen

## Next Tasks
- Build new Jessica Lazarus structure (this file!)
- Push to GitHub BruceMotorsport/lazarus
- Fix BruceClaw installer

---
*Status updated automatically*
