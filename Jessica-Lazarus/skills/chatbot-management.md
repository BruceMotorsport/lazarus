# Skill: Chatbot Management

## What It Does
Manages the Bruce Racing and GoGetter Digital chatbot at bruce-racing-pvt.web.app/chat.html

## Architecture
- **Frontend:** chat.html on Firebase Hosting (bruce-racing-pvt.web.app)
- **Backend:** gogetter-engine.vercel.app/api/chat (Next.js API route)
- **LLM:** Groq qwen/qwen3.6-27b (free tier)

## How to Update Chatbot

### Change System Prompts
Edit `chat.html` in `projects/bruce-racing-new/`:
```javascript
const systemPrompt = currentMode === 'racing' 
  ? 'You are Bruce Racing AI assistant...'
  : 'You are Gogetter Digital AI assistant...';
```

### Change LLM Model
Edit `app/api/chat/route.ts` in `projects/gogetter-engine/`:
```typescript
model: "qwen/qwen3.6-27b"  // Groq model name
```

### Deploy Changes
```bash
# Frontend (chat.html)
cd projects/bruce-racing-new && firebase deploy --only hosting:bruce-racing-pvt

# Backend (API)
cd projects/gogetter-engine && npx vercel --prod --yes
```

## Current Config
- **Bruce Racing prompt:** 4x4 diesel workshop, Rs6,500/hr, Kaduwela
- **GoGetter Digital prompt:** websites, apps, platforms
- **Fallback:** "Call us on0772256655"

## Known Issues
- Qwen models output `` tags — stripped with regex
- TTS reads markdown symbols — stripped before speaking
- GLM banned (privacy violation)

---
*Last updated:2026-08-18*
