# QuantView 24/7 Render Deployment Guide

This guide explains how to deploy QuantView (Frontend + Backend + RAG Intelligence System) on Render.com to run 24/7 in production.

---

## 1. Architecture Overview on Render

```
                        ┌──────────────────────────────┐
                        │   Render Web Service (UI)    │
                        │   Next.js (Port 3000)        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼ HTTP / API
                        ┌──────────────────────────────┐
                        │ Render Backend Web Service   │
                        │ FastAPI (Uvicorn Port 8000)  │
                        └──────┬───────────────┬───────┘
                               │               │
            ┌──────────────────┴──┐         ┌──┴──────────────────┐
            │ PostgreSQL (Neon)   │         │ Gemini / OpenRouter │
            │ Operational DB      │         │ Cloud LLM Provider  │
            └─────────────────────┘         └─────────────────────┘
```

---

## 2. Setting Up Backend Web Service on Render

1. Go to **Render Dashboard** $\rightarrow$ **New** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository (`https://github.com/EvilDocter/quantview`).
3. Set the configuration options:

| Configuration Field | Value |
| :--- | :--- |
| **Name** | `quantview-backend` |
| **Root Directory** | `backend-india` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. **Environment Variables** (in Render Environment Tab):

```env
APP_ENV=production
FRONTEND_URL=https://quantview-frontend.onrender.com
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<dbname>
DATABASE_URL_SYNC=postgresql://<user>:<password>@<host>/<dbname>

# Cloud AI Provider for 24/7 Operation
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
LLM_REASONING_MODEL=gemini-2.5-flash
LLM_EXTRACTION_MODEL=gemini-2.5-flash
```

> [!NOTE]
> Since Render cloud instances cannot directly reach intranet IP `10.250.101.68` without an SSH/ngrok tunnel, setting `LLM_PROVIDER=gemini` ensures fast, reliable, 24/7 AI response generation on Render!

---

## 3. Setting Up Frontend Web Service on Render

1. Go to **Render Dashboard** $\rightarrow$ **New** $\rightarrow$ **Web Service**.
2. Select your GitHub repository (`quantview`).
3. Set the configuration options:

| Configuration Field | Value |
| :--- | :--- |
| **Name** | `quantview-frontend` |
| **Root Directory** | `frontend` |
| **Environment** | `Node` |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm start` |

4. **Environment Variables**:

```env
NEXT_PUBLIC_BACKEND_URL=https://quantview-backend.onrender.com
```

---

## 4. How to Expose Local Ollama GPU Server to Render (Optional)

If you wish to route Render AI requests back to your GPU server (`10.250.101.68` on Ollama port `11434`), set up a **Cloudflare Tunnel** or **ngrok**:

1. On your GPU server (`10.250.101.68`):
   ```bash
   cloudflared tunnel --url http://localhost:11434
   ```
2. Copy the public URL generated (e.g. `https://ollama-gpu-tunnel.trycloudflare.com`).
3. Set `AI_SERVER_URL` in Render Environment Variables:
   ```env
   AI_SERVER_URL=https://ollama-gpu-tunnel.trycloudflare.com/api/generate
   LLM_PROVIDER=ollama
   ```

---

## 5. Verification Checklist

- [x] Backend responds to `GET /health` with HTTP 200.
- [x] AI Research API `POST /api/v1/ai/research` generates full reports with RAG citations.
- [x] QuantLab page is hidden from navigation bar.
- [x] Frontend builds cleanly via `npm run build`.
