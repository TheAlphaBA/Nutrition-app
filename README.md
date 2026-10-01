# 🥦 NutriBot — AI Nutrition Assistant (Milestone 1)

An AI-powered chatbot that answers questions about food, nutrition, and food safety using structured, claim-based responses with deterministic code-enforced guardrails.

---

## 🌟 Milestone 1 Highlights

- **Structured Claim Extraction**: Every answer is decomposed into individual factual claims with explicit source metadata (`source: null` in Milestone 1, ready for RAG citations in Milestone 2).
- **Dual AI Engine Support**: Works natively with **Google Gemini** (`gemini-3.1-flash-lite`, `gemini-3.8-flash`) via strict JSON output, with automatic multi-model fallback and optional OpenAI (`gpt-4o`) support.
- **Code-Enforced Guardrails (100% Deterministic)**: Pre-filters queries to block calorie targets, body weight/BMI recommendations, and medical advice before reaching the LLM.
- **Modern Next.js Frontend**: Sleek dark-mode emerald interface, interactive claim badges, slide-out Sources Drawer, suggestion chips, and responsive consultation sidebar.
- **Comprehensive Evaluation**: 30 live test executions across 10 evaluation questions with automated failure logging into SQLite and scorecard generation.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | Next.js 16 (App Router), React 19, Vanilla CSS | Responsive chat UI, claim cards, sources drawer |
| **Backend** | FastAPI, Python 3.9+, Pydantic v2 | REST API, async thread pooling, lifespan DB init |
| **Database** | SQLite + SQLAlchemy ORM | Conversations, Messages, Claims, FailureLogs |
| **AI / LLM** | Google Gemini (Free Tier) / OpenAI GPT-4o | Structured JSON generation |
| **Guardrails** | Python regex engine (Pre-filter) | Zero-hallucination deterministic safety layer |
| **Deployment** | Dockerfile, Procfile, Vercel | One-click cloud deployment ready |

---

## 📁 Repository Structure

```
├── frontend/                  # Next.js App Router frontend
│   ├── app/
│   │   ├── globals.css        # Comprehensive design system
│   │   ├── layout.tsx         # Root layout & SEO metadata
│   │   └── page.tsx           # Page assembly & state management
│   ├── components/            # UI Components
│   │   ├── ChatWindow.tsx     # Message list & empty hero state
│   │   ├── MessageBubble.tsx  # Formatted messages & guardrail badges
│   │   ├── ClaimBadge.tsx     # Interactive claim cards (M1 unverified)
│   │   ├── SourcesPanel.tsx   # Slide-out sources & citation panel
│   │   ├── Sidebar.tsx        # Conversation history & thread switcher
│   │   ├── Header.tsx         # Branding, model status & sources toggle
│   │   └── InputBar.tsx       # Auto-expanding textarea & suggestion chips
│   └── lib/api.ts             # Backend API client
├── backend/                   # FastAPI backend server
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & CORS
│   │   ├── config.py          # Environment settings (Pydantic)
│   │   ├── models/database.py # SQLAlchemy models & session factory
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── prompts/           # NutriBot system persona & boundaries
│   │   ├── services/
│   │   │   ├── llm_service.py # Gemini & OpenAI structured completion
│   │   │   └── guardrails.py  # Code-enforced regex safety filter
│   │   └── routers/chat.py    # POST /api/chat, GET /api/conversations
│   ├── scripts/
│   │   ├── seed_database.py   # Populates database with sample threads
│   │   └── run_failure_tests.py # 30-run automated test suite
│   ├── tests/                 # Unit test suite (18 tests, 100% pass)
│   ├── Dockerfile             # Production container definition
│   └── Procfile               # Cloud deployment web process
├── data/
│   ├── seed_conversations.json# 6 seed conversations (68 claims)
│   ├── test_questions.json    # 10 evaluation test questions
│   └── guardrail_test_cases.json # 30 guardrail test cases
├── docs/                      # Full project specifications
│   ├── problemStatement.md
│   ├── architecture.md
│   ├── implementation-plan.md
│   ├── edge-cases.md
│   ├── eval.md
│   └── eval-report.md         # Automated Phase 6 test scorecard
└── README.md
```

---

## 🚀 Quickstart (Local Development)

### 1. Backend Setup

```bash
# From project root
cd backend

# Create and activate virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Configure your Gemini API key in backend/.env:
# GEMINI_API_KEY=your_key_here

# Start the FastAPI server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

* API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
* Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Frontend Setup

```bash
# In a new terminal from project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

* Web Application: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Testing & Evaluation

### Run Backend Unit Tests (18 tests)

```bash
PYTHONPATH=backend python3 -m unittest discover -s backend/tests
```

### Run 30-Run Live Evaluation Suite

```bash
PYTHONPATH=backend python3 backend/scripts/run_failure_tests.py
```

* Results are automatically logged into the SQLite `failure_logs` table and compiled into [docs/eval-report.md](docs/eval-report.md).

---

## ☁️ Deployment Guide

### Deploy Backend (Railway / Render)
1. Push this repository to GitHub.
2. In [Railway](https://railway.app), click **New Project** → **Deploy from GitHub repo**.
3. Set the Root Directory to `backend/`.
4. Add environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `ENVIRONMENT`: `production`
   - `CORS_ORIGINS`: Your Vercel frontend URL
5. Deploy! Railway will automatically detect the `Dockerfile` or `Procfile`.

### Deploy Frontend (Vercel)
1. In [Vercel](https://vercel.com), click **Add New** → **Project** → Import your repository.
2. Set Root Directory to `frontend`.
3. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL`: `https://your-railway-backend.up.railway.app/api`
4. Click **Deploy**.

---

## 📄 License
MIT
