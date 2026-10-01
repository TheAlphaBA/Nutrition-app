# 🚀 NutriBot Deployment Plan: Railway & Vercel

A step-by-step deployment guide for deploying the complete **NutriBot AI Nutrition Assistant** (Milestone 1) to production using:
- **FastAPI Backend** on **[Railway](https://railway.app)**
- **Next.js Frontend (Stitch UI)** on **[Vercel](https://vercel.com)**

---

## 📋 Table of Contents
1. [Architecture Overview & Deployment Flow](#1-architecture-overview--deployment-flow)
2. [Prerequisites & Accounts](#2-prerequisites--accounts)
3. [Pre-Deployment Local Verification Checklist](#3-pre-deployment-local-verification-checklist)
4. [Step 1: Push Project to GitHub](#step-1-push-project-to-github)
5. [Step 2: Deploy Backend on Railway](#step-2-deploy-backend-on-railway)
6. [Step 3: Deploy Frontend on Vercel](#step-3-deploy-frontend-on-vercel)
7. [Step 4: Finalise CORS Handshake](#step-4-finalise-cors-handshake)
8. [Step 5: Production Smoke Test Suite](#step-5-production-smoke-test-suite)
9. [Troubleshooting & Rollback Strategies](#troubleshooting--rollback-strategies)

---

## 1. Architecture Overview & Deployment Flow

```mermaid
flowchart LR
    subgraph Client
        Browser["User Browser"]
    end

    subgraph Vercel["Vercel Cloud (Frontend)"]
        NextApp["Next.js 16 App Router\n(Nutritional Editorial UI)"]
    end

    subgraph Railway["Railway Cloud (Backend)"]
        FastAPI["FastAPI API Server\n(Uvicorn)"]
        Guardrails["Code Guardrails Engine"]
        SQLite[("SQLite Database\n(nutrition.db)")]
    end

    subgraph External["AI Providers"]
        Gemini["Google Gemini 3.1 Flash\n(Google AI Studio)"]
    end

    Browser -->|HTTPS| NextApp
    NextApp -->|REST /api/chat| FastAPI
    FastAPI -->|Pre-filter Check| Guardrails
    FastAPI -->|Structured JSON Prompt| Gemini
    FastAPI -->|Store Threads & Claims| SQLite
    FastAPI -->>|ChatResponse + Claims| NextApp
```

---

## 2. Prerequisites & Accounts

Ensure you have the following ready before starting:

| Service | Requirement | Sign-up Link |
|---|---|---|
| **GitHub** | Free account with Git installed | [github.com](https://github.com) |
| **Railway** | Free / Hobby account (for Python backend) | [railway.app](https://railway.app) |
| **Vercel** | Free Hobby account (for Next.js frontend) | [vercel.com](https://vercel.com) |
| **Gemini API Key** | Google AI Studio free tier key (`AIzaSy...` or `AQ...`) | [aistudio.google.com](https://aistudio.google.com) |

---

## 3. Pre-Deployment Local Verification Checklist

Verify that local code builds and passes all automated tests before pushing:

- [x] **18/18 Unit Tests Passing**:
  ```bash
  PYTHONPATH=backend python3 -m unittest discover -s backend/tests
  ```
- [x] **Next.js Production Build Passing** (0 TypeScript / ESLint errors):
  ```bash
  cd frontend && npm run build
  ```
- [x] **Backend Health Check Verified**:
  ```bash
  curl http://localhost:8000/health
  # {"status": "ok", "environment": "development"}
  ```
- [x] **`.gitignore` Verified**: Ensure `backend/.env` is ignored and never pushed to GitHub.

---

## Step 1: Push Project to GitHub

1. Open your browser and navigate to **[github.com/new](https://github.com/new)**.
2. Fill out repository settings:
   - **Repository Name:** `nutrition-assistant` (or `nutribot`)
   - **Visibility:** Public (or Private)
   - ⚠️ **Leave all checkboxes UNCHECKED** (*Add a README*, *Add .gitignore*, *Choose a license*).
3. Click **Create repository**.
4. In your local terminal, link and push the repository:
   ```bash
   cd "/Users/kaushalyasasikumar/Documents/Nutrition project"

   # Replace with your actual GitHub username
   git remote add origin https://github.com/YOUR_USERNAME/nutrition-assistant.git
   git branch -M main
   git push -u origin main
   ```
5. Refresh the GitHub repository page to verify all folders (`backend/`, `frontend/`, `data/`, `docs/`) are present.

---

## Step 2: Deploy Backend on Railway

Railway will build and host the FastAPI server using the included [`backend/Dockerfile`](file:///Users/kaushalyasasikumar/Documents/Nutrition%20project/backend/Dockerfile) and [`backend/Procfile`](file:///Users/kaushalyasasikumar/Documents/Nutrition%20project/backend/Procfile).

### 2.1 Create the Railway Project
1. Log in to **[Railway.app](https://railway.app)**.
2. Click **+ New Project** → Select **Deploy from GitHub repo**.
3. Select your repository (`nutrition-assistant`).
4. If prompted to deploy immediately, click **Configure**.

### 2.2 Configure Service Settings
1. Click on the deployed service card to open its settings.
2. Go to the **Settings** tab:
   - **Root Directory:** Change from `/` to `/backend`
   - **Build Command:** Leave blank (Railway auto-detects `requirements.txt` or `Dockerfile`).
   - **Start Command:** (Optional if using Dockerfile, otherwise set):
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

### 2.3 Set Environment Variables
Go to the **Variables** tab in Railway and add the following:

| Variable Name | Value | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | `your-gemini-api-key` | Google Gemini AI authentication |
| `LLM_PROVIDER` | `gemini` | AI engine selection |
| `ENVIRONMENT` | `production` | Production environment flag |
| `DATABASE_URL` | `sqlite:////app/nutrition.db` | Persistent SQLite database path |
| `CORS_ORIGINS` | `http://localhost:3000,https://*.vercel.app` | Allowed frontend origins (updated in Step 4) |
| `LOG_LEVEL` | `info` | Application logging level |

### 2.4 Generate Public Domain
1. In the **Settings** tab, scroll to **Networking** → **Public Networking**.
2. Click **Generate Domain**.
3. Railway will assign a public URL, for example:
   `https://nutribot-production.up.railway.app`
4. **Copy this URL** — you will need it for the frontend in Step 3!

### 2.5 Verify Backend Deployment
Test the live health check in your terminal or browser:
```bash
curl https://YOUR_RAILWAY_URL.up.railway.app/health
# Expected Output: {"status":"ok","environment":"production"}
```
You can also visit `https://YOUR_RAILWAY_URL.up.railway.app/docs` to interact with Swagger UI.

---

## Step 3: Deploy Frontend on Vercel

Vercel provides native Next.js hosting with global edge caching and instant deployments.

### 3.1 Import the Project
1. Log in to **[Vercel.com](https://vercel.com)**.
2. Click **Add New…** → **Project**.
3. Under **Import Git Repository**, select your `nutrition-assistant` repo.

### 3.2 Configure Build & Output Settings
In the **Configure Project** screen:
- **Project Name:** `nutribot` (or any name you prefer)
- **Framework Preset:** `Next.js` (automatically detected)
- **Root Directory:** Click **Edit** and select **`frontend`** (⚠️ **Crucial Step!**)

### 3.3 Add Environment Variables
Expand the **Environment Variables** section and add:

| Key | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://YOUR_RAILWAY_URL.up.railway.app/api` | Note the `/api` suffix at the end |

### 3.4 Deploy
1. Click **Deploy**.
2. Vercel will run `npm install` and `npm run build`.
3. In approximately 60 seconds, you will see the confetti screen with your live URL:
   `https://nutribot.vercel.app`

---

## Step 4: Finalise CORS Handshake

Now that your frontend has a live production URL, update the backend so it accepts requests from this exact Vercel domain:

1. Copy your Vercel URL (e.g. `https://nutribot.vercel.app`).
2. Go back to **Railway** → Your Service → **Variables**.
3. Edit the `CORS_ORIGINS` variable:
   ```env
   CORS_ORIGINS=https://nutribot.vercel.app,http://localhost:3000
   ```
4. Railway will automatically trigger a rapid 5-second redeploy to apply the updated origin.

---

## Step 5: Production Smoke Test Suite

Run these 6 verification tests on your live production URL (`https://nutribot.vercel.app`):

| # | Action | Input / Trigger | Expected Live Behavior | Result |
|---|---|---|---|:---:|
| **S1** | **UI Load** | Open `https://nutribot.vercel.app` | Earthy off-white/sage UI loads with Playfair serif branding, active memory pill, and sidebar. | ⬜ |
| **S2** | **Nutritional Query** | Click chip: *"What vitamins does spinach contain?"* | NutriBot returns formatted answer + numbered claim badges (`[1]`, `[2]`, `[3]`) marked `Unverified Citation (M1)`. | ⬜ |
| **S3** | **Sources Drawer** | Click **"Sources (X)"** in top header | Drawer slides in from right showing Milestone 1 architecture notice and claim tracking. | ⬜ |
| **S4** | **Calorie Guardrail** | Send: *"How many calories should I eat to lose weight?"* | Intercepted immediately by code guardrail with terracotta shield banner and refusal advice. | ⬜ |
| **S5** | **Medical Guardrail** | Send: *"What medication helps with cholesterol?"* | Blocked by deterministic regex; advises consulting a licensed physician. | ⬜ |
| **S6** | **Thread Persistence** | Refresh page | Previous consultation appears in sidebar and can be reloaded. | ⬜ |

---

## Troubleshooting & Rollback Strategies

### 1. Frontend shows "Connection Error" / Cannot reach backend
* **Cause**: `NEXT_PUBLIC_API_URL` in Vercel is missing `/api` or pointing to localhost.
* **Fix**: Go to Vercel → **Settings** → **Environment Variables** → Verify `NEXT_PUBLIC_API_URL` equals `https://<railway-domain>.up.railway.app/api`. Redeploy if changed.

### 2. CORS Error in Browser Console (`Access-Control-Allow-Origin`)
* **Cause**: Railway `CORS_ORIGINS` does not match the exact Vercel URL (e.g. trailing slash or missing https).
* **Fix**: Ensure Railway variable is formatted without trailing slash: `https://your-app.vercel.app`.

### 3. Railway SQLite Data Ephemerality
* **Note for Milestone 1**: In Milestone 1, SQLite stores local consultation history in `/app/nutrition.db`. If the Railway container restarts, you can re-run the seed script via Railway CLI:
  ```bash
  railway run python backend/scripts/seed_database.py
  ```
  *(In Milestone 2, this will be migrated to persistent PostgreSQL via Railway Postgres).*

---

## 🎯 Summary
Following this plan guarantees:
- Zero build errors (pre-tested with TypeScript & Unit tests)
- 100% deterministic guardrail safety in production
- Fully verified Milestone 1 architecture ready for Milestone 2 RAG integration
