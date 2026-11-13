# CineFlow AI — Describe it. Direct it. Create it.

MVP (Phase 1): idea → AI Director → editable shot-by-shot storyboard.

- `backend/` FastAPI (runs as a Vercel Python function). `POST /api/storyboard`, `POST /api/scene/regenerate`, `GET /api/health`. Uses Claude when `ANTHROPIC_API_KEY` is set, otherwise returns a demo storyboard.
- `frontend/` Next.js 14 + TypeScript. Create screen + storyboard editor (edit / regenerate / delete / add scene).
- `backend/app/providers.py` is the video provider layer for Phase 2.

## Run locally
```
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && cp .env.example .env.local && npm run dev
```

## Deploy (everything on Vercel)
Create two Vercel projects from the same GitHub repo.

**1. Backend project** — Root Directory `backend`. Environment variables: `ANTHROPIC_API_KEY`, `CORS_ORIGINS=https://<frontend-domain>`, optional `CORS_ORIGIN_REGEX=https://.*\.vercel\.app`. Function timeout is set to 60s in `backend/vercel.json` (needed for AI generation).

**2. Frontend project** — Root Directory `frontend`. Environment variable: `NEXT_PUBLIC_API_URL=https://<backend-domain>`.

Verify: `curl https://<backend-domain>/api/health` returns `{"status":"ok","ai":true}`.
Redeploy the frontend after setting `NEXT_PUBLIC_API_URL` (it is baked in at build time).
