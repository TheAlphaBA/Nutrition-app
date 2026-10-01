# 🥦 AI Nutrition Assistant

An AI-powered chatbot that answers questions about food, nutrition, and food safety using structured, claim-based responses.

## Project Overview

This project builds a nutrition assistant that returns structured output — breaking every response into verifiable claims with source fields. Milestone 1 uses LLM-memory-only answers (no RAG), establishing the full architecture for Milestone 2's retrieval layer.

## Tech Stack

| Layer        | Technology                                     |
| ------------ | ---------------------------------------------- |
| **Frontend** | Next.js (App Router)                           |
| **Backend**  | FastAPI (Python)                               |
| **LLM**      | OpenAI API (Structured Output)                 |
| **Database** | SQLite (M1) → Postgres (M2)                   |
| **Hosting**  | Vercel (frontend) + Railway (backend)          |

## Project Structure

```
├── frontend/          # Next.js chat interface
├── backend/           # FastAPI API server
│   ├── app/
│   │   ├── main.py          # App entry point
│   │   ├── config.py        # Environment config
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic (LLM, guardrails)
│   │   ├── schemas/         # Pydantic models
│   │   ├── models/          # SQLAlchemy models
│   │   └── prompts/         # System prompt
│   ├── scripts/             # Utility scripts
│   └── tests/               # Test suite
├── data/              # Seed data & test datasets
├── docs/              # Documentation
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit .env with your API key
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Verify Setup

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "ok", "environment": "development"}
```

## Key Features

- **Structured Responses** — Every answer is broken into individual claims with source fields
- **Code-Enforced Guardrails** — Blocks calorie targets, weight recommendations, and medical advice via application logic
- **Claim Tracking** — Each factual claim is stored separately for future verification (M2)
- **Sources Panel** — UI panel ready for M2's cited sources (empty in M1)

## Documentation

- [Problem Statement](docs/problemStatement.md)
- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Edge Cases](docs/edge-cases.md)
- [Evaluation Plan](docs/eval.md)

## Live URLs

> _To be updated after deployment (Phase 7)_

- **Frontend:** `https://[pending].vercel.app`
- **Backend:** `https://[pending].railway.app`

## License

MIT
