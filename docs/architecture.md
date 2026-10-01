# Architecture: AI Nutrition Assistant (Milestone 1)

> Derived from [problemStatement.md](file:///Users/kaushalyasasikumar/Documents/Nutrition%20project/docs/problemStatement.md)

---

## 1. High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend (Next.js)"]
        UI["Chat UI"]
        SP["Sources Panel"]
        MS["Message Store (React State)"]
    end

    subgraph Server["Backend (FastAPI)"]
        API["POST /api/chat"]
        GR["Guardrail Engine"]
        LLM["LLM Service"]
        SC["Schema Validator"]
    end

    subgraph External["External Services"]
        OAI["OpenAI API (Structured Output)"]
    end

    subgraph Storage["Database (SQLite)"]
        CONV["conversations"]
        MSG["messages"]
        CL["claims"]
        FL["failure_logs"]
    end

    UI -->|user message| API
    API -->|input text| GR
    GR -->|blocked| API
    GR -->|passed| LLM
    LLM -->|structured prompt + schema| OAI
    OAI -->|JSON response| LLM
    LLM -->|raw response| SC
    SC -->|validated response| API
    API -->|persist| MSG
    API -->|persist| CL
    API -->|answer + claims| UI
    SP -->|"reads claims[].source (null in M1)"| MS
```

---

## 2. Tech Stack Decisions

| Layer          | Technology        | Rationale                                                        |
| -------------- | ----------------- | ---------------------------------------------------------------- |
| **Frontend**   | Next.js (App Router) | Server components for SEO, API routes as optional BFF proxy   |
| **Backend**    | FastAPI (Python)  | Async-native, Pydantic models for schema validation, fast dev    |
| **LLM**        | OpenAI API        | Native Structured Output mode (`response_format: json_schema`)   |
| **Database**   | SQLite            | Zero-config for M1; swappable to Postgres/Supabase in M2        |
| **ORM**        | SQLAlchemy        | Mature, async support, easy migration path                       |
| **Deployment** | Vercel (FE) + Railway (BE) | Free-tier friendly, public URL requirement met            |
| **VCS**        | GitHub            | Required per problem statement                                   |

---

## 3. Project Structure

```
nutrition-assistant/
├── frontend/                      # Next.js application
│   ├── app/
│   │   ├── layout.tsx             # Root layout with metadata
│   │   ├── page.tsx               # Main chat page
│   │   └── globals.css            # Global styles
│   ├── components/
│   │   ├── ChatWindow.tsx         # Message list + scroll behaviour
│   │   ├── MessageBubble.tsx      # Individual message rendering
│   │   ├── InputBar.tsx           # Text input + send button
│   │   ├── SourcesPanel.tsx       # Right-side sources panel (empty M1)
│   │   └── ClaimBadge.tsx         # Renders individual claim chips
│   ├── lib/
│   │   ├── api.ts                 # HTTP client for backend calls
│   │   └── types.ts               # Shared TypeScript interfaces
│   ├── package.json
│   └── next.config.js
│
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── main.py                # FastAPI app entry point, CORS config
│   │   ├── routers/
│   │   │   └── chat.py            # POST /api/chat endpoint
│   │   ├── services/
│   │   │   ├── llm_service.py     # OpenAI API integration
│   │   │   └── guardrails.py      # Code-enforced topic guardrails
│   │   ├── schemas/
│   │   │   ├── request.py         # Pydantic request models
│   │   │   └── response.py        # Pydantic response models (answer, claims)
│   │   ├── models/
│   │   │   └── database.py        # SQLAlchemy models + engine
│   │   ├── prompts/
│   │   │   └── system_prompt.py   # System prompt definition
│   │   └── config.py              # Environment variables, settings
│   ├── tests/
│   │   ├── test_questions.py      # 10 test questions across 4 categories
│   │   └── failure_log.py         # Failure logging runner + recorder
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   ├── problemStatement.md
│   └── architecture.md            # This file
├── .gitignore
└── README.md
```

---

## 4. Database Schema

```mermaid
erDiagram
    conversations {
        string id PK "UUID"
        datetime created_at
        datetime updated_at
    }

    messages {
        string id PK "UUID"
        string conversation_id FK
        string role "user | assistant"
        text content "raw text for user, answer text for assistant"
        datetime created_at
    }

    claims {
        string id PK "UUID"
        string message_id FK
        text claim_text
        text source "nullable — always null in M1"
    }

    failure_logs {
        string id PK "UUID"
        string test_question_id
        string category "nutrient | safety | cooking | ambiguous"
        text question
        text response_snapshot
        string failure_type "unbacked_claim | shifting_number | fake_citation | guardrail_fail | hedged_answer"
        int run_number
        datetime logged_at
    }

    conversations ||--o{ messages : has
    messages ||--o{ claims : contains
```

### SQLAlchemy Models (Python)

```python
# backend/app/models/database.py

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")
    claims = relationship("Claim", back_populates="message")

class Claim(Base):
    __tablename__ = "claims"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    source = Column(Text, nullable=True)  # Always null in M1
    message = relationship("Message", back_populates="claims")

class FailureLog(Base):
    __tablename__ = "failure_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_question_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    response_snapshot = Column(Text, nullable=False)
    failure_type = Column(String, nullable=False)
    run_number = Column(Integer, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)
```

---

## 5. API Design

### 5.1 Endpoints

| Method | Path              | Description                          | Auth |
| ------ | ----------------- | ------------------------------------ | ---- |
| POST   | `/api/chat`       | Send a message, receive structured response | None (M1) |
| GET    | `/api/conversations/{id}` | Retrieve conversation history | None (M1) |
| POST   | `/api/conversations` | Create a new conversation         | None (M1) |

### 5.2 Request / Response Schemas

**POST `/api/chat` — Request**

```json
{
  "conversation_id": "uuid-string",
  "message": "What are the health benefits of spinach?"
}
```

**POST `/api/chat` — Response**

```json
{
  "conversation_id": "uuid-string",
  "message_id": "uuid-string",
  "answer": "Spinach is a nutrient-dense leafy green vegetable...",
  "claims": [
    {
      "text": "Spinach is rich in iron, providing about 2.7 mg per 100g serving.",
      "source": null
    },
    {
      "text": "Spinach contains high levels of vitamin K, important for blood clotting.",
      "source": null
    }
  ],
  "guardrail_triggered": false
}
```

**Guardrail-blocked Response**

```json
{
  "conversation_id": "uuid-string",
  "message_id": "uuid-string",
  "answer": "I'm unable to provide specific calorie targets as this requires personalised medical assessment.",
  "claims": [],
  "guardrail_triggered": true,
  "guardrail_reason": "calorie_weight_target"
}
```

### 5.3 LLM Structured Output Schema

Sent to the OpenAI API via `response_format`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "nutrition_response",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "answer": {
          "type": "string",
          "description": "The complete answer text"
        },
        "claims": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "text": {
                "type": "string",
                "description": "A single factual claim made in the answer"
              },
              "source": {
                "type": ["string", "null"],
                "description": "Source URL or citation. Must be null for Milestone 1."
              }
            },
            "required": ["text", "source"]
          }
        }
      },
      "required": ["answer", "claims"]
    }
  }
}
```

---

## 6. Guardrail Engine (Code-Enforced)

The guardrail system operates as a **pre-processing filter** before the user's message reaches the LLM. This is a hard requirement — the system prompt may also reinforce these rules, but the code-level check is the primary enforcement mechanism.

### 6.1 Architecture

```mermaid
flowchart LR
    INPUT["User Message"] --> KW["Keyword / Pattern Matcher"]
    KW -->|match found| BLOCK["Return Refusal Response"]
    KW -->|no match| INTENT["Intent Classifier (regex + heuristics)"]
    INTENT -->|flagged| BLOCK
    INTENT -->|safe| LLM["Forward to LLM"]
```

### 6.2 Blocked Categories

| Category                | Detection Strategy                                         | Example Triggers                                      |
| ----------------------- | ---------------------------------------------------------- | ----------------------------------------------------- |
| Calorie / weight targets| Regex patterns for calorie counts, daily intake goals      | "how many calories should I eat", "caloric intake for" |
| Body weight recommendations | Keyword matching + intent heuristics                  | "ideal weight", "should I weigh", "BMI for my height" |
| Medical advice          | Medical terminology detection + advice-seeking patterns    | "should I take", "treat my", "cure for", "medication" |

### 6.3 Implementation Approach

```python
# backend/app/services/guardrails.py

import re
from dataclasses import dataclass
from enum import Enum

class GuardrailCategory(str, Enum):
    CALORIE_WEIGHT_TARGET = "calorie_weight_target"
    BODY_WEIGHT_RECOMMENDATION = "body_weight_recommendation"
    MEDICAL_ADVICE = "medical_advice"

@dataclass
class GuardrailResult:
    blocked: bool
    category: GuardrailCategory | None = None
    reason: str | None = None

PATTERNS = {
    GuardrailCategory.CALORIE_WEIGHT_TARGET: [
        r"how many calories should (I|i|we)",
        r"calor(ie|ic) (target|goal|intake|budget|limit) for (me|my)",
        r"daily caloris?e?s? (for|to)",
        r"how many calories (do i|should i|to) (need|eat|consume)",
    ],
    GuardrailCategory.BODY_WEIGHT_RECOMMENDATION: [
        r"(ideal|healthy|target|goal) weight for",
        r"how much should (I|i|a person) weigh",
        r"what should (I|my) (weight|bmi) be",
        r"(lose|gain) weight .*(plan|diet|program)",
    ],
    GuardrailCategory.MEDICAL_ADVICE: [
        r"should (I|i) take .*(supplement|medication|medicine|drug|pill)",
        r"(treat|cure|remedy|fix) (my|the|a) .*(condition|disease|illness|disorder)",
        r"(prescri|diagnos)",
        r"medical advice for",
    ],
}

REFUSAL_MESSAGES = {
    GuardrailCategory.CALORIE_WEIGHT_TARGET: (
        "I'm unable to provide specific calorie or weight targets. "
        "These depend on individual factors that require assessment by a "
        "qualified healthcare professional or registered dietitian."
    ),
    GuardrailCategory.BODY_WEIGHT_RECOMMENDATION: (
        "I'm unable to recommend what a person should weigh. "
        "Healthy weight varies significantly based on individual factors. "
        "Please consult a healthcare provider for personalised guidance."
    ),
    GuardrailCategory.MEDICAL_ADVICE: (
        "I'm unable to provide medical advice, including recommendations "
        "about medications, supplements for specific conditions, or treatment plans. "
        "Please consult a qualified healthcare professional."
    ),
}

def check_guardrails(user_message: str) -> GuardrailResult:
    """Pre-LLM guardrail check. Returns blocked=True if the message
    falls into a prohibited category."""
    text = user_message.lower()
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardrailResult(
                    blocked=True,
                    category=category,
                    reason=REFUSAL_MESSAGES[category],
                )
    return GuardrailResult(blocked=False)
```

---

## 7. System Prompt Design

```python
# backend/app/prompts/system_prompt.py

SYSTEM_PROMPT = """
You are NutriBot, an AI Nutrition Assistant. You answer questions about
food, nutrition, and food safety based on general nutritional knowledge.

## Role
- You are a helpful, accurate nutrition information assistant.
- You are NOT a doctor, dietitian, or medical professional.

## Response Rules
1. Keep answers concise (2-4 paragraphs maximum).
2. Break your answer into individual factual claims.
3. Be specific with numbers when referencing nutrient values (e.g., RDA values).
4. If you are uncertain, say so explicitly — do not fabricate data.
5. Every claim source must be null — do not invent citations or references.

## Strict Boundaries (DO NOT ANSWER)
- Do NOT provide calorie targets or daily calorie recommendations.
- Do NOT recommend what a person should weigh or provide BMI-based advice.
- Do NOT provide medical advice, diagnoses, or treatment recommendations.
- If asked about these topics, respond with a polite refusal and suggest
  consulting a qualified healthcare professional.

## Output Format
You MUST respond in the structured JSON schema provided. Do not add any
text outside the JSON structure.
"""
```

---

## 8. Request Lifecycle

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant FE as Next.js Frontend
    participant BE as FastAPI Backend
    participant GR as Guardrail Engine
    participant LLM as OpenAI API
    participant DB as SQLite

    U->>FE: Types message, clicks Send
    FE->>BE: POST /api/chat {conversation_id, message}
    BE->>DB: Create/validate conversation
    BE->>DB: Store user message
    BE->>GR: check_guardrails(message)

    alt Guardrail Triggered
        GR-->>BE: GuardrailResult(blocked=True, category, reason)
        BE->>DB: Store refusal as assistant message
        BE-->>FE: {answer: refusal, claims: [], guardrail_triggered: true}
    else Guardrail Passed
        GR-->>BE: GuardrailResult(blocked=False)
        BE->>LLM: Chat completion (system_prompt + history + user_msg, json_schema)
        LLM-->>BE: Structured JSON {answer, claims[{text, source: null}]}
        BE->>BE: Validate response against Pydantic schema
        BE->>DB: Store assistant message
        BE->>DB: Store individual claims
        BE-->>FE: {answer, claims, guardrail_triggered: false}
    end

    FE->>U: Render answer + claim badges + sources panel
```

---

## 9. Frontend Component Architecture

```mermaid
flowchart TB
    subgraph Page["app/page.tsx"]
        Layout["Two-Column Layout"]
    end

    subgraph Left["Left Column (Chat)"]
        CW["ChatWindow"]
        CW --> MB1["MessageBubble (user)"]
        CW --> MB2["MessageBubble (assistant)"]
        MB2 --> CB["ClaimBadge × N"]
        IB["InputBar"]
    end

    subgraph Right["Right Column"]
        SP["SourcesPanel"]
        SP --> Empty["'No sources yet' placeholder (M1)"]
    end

    Page --> Left
    Page --> Right
```

### Component Responsibilities

| Component        | Responsibility                                                       |
| ---------------- | -------------------------------------------------------------------- |
| `ChatWindow`     | Scrollable message list, auto-scroll on new messages                 |
| `MessageBubble`  | Renders a single message (user or assistant), shows claim badges for assistant |
| `ClaimBadge`     | Clickable chip showing claim text; highlights in sources panel (M2)  |
| `InputBar`       | Text input + send button, disabled during loading                    |
| `SourcesPanel`   | Right panel listing sources for selected claims; empty in M1         |

---

## 10. Failure Testing Framework

### 10.1 Test Questions (10 across 4 categories)

| #  | Category             | Question                                                              |
| -- | -------------------- | --------------------------------------------------------------------- |
| 1  | Nutrient requirements | "How much vitamin C does an adult need daily?"                       |
| 2  | Nutrient requirements | "What is the recommended daily intake of protein for a 70kg adult?"  |
| 3  | Nutrient requirements | "How much iron do women need per day compared to men?"               |
| 4  | Food safety          | "How long can cooked rice be safely stored in the fridge?"           |
| 5  | Food safety          | "At what temperature should chicken be cooked to be safe?"           |
| 6  | Cooking methods      | "Does boiling vegetables destroy their vitamins?"                    |
| 7  | Cooking methods      | "Is it safe to eat medium-rare steak?"                               |
| 8  | Cooking methods      | "Does microwaving food reduce its nutritional value?"                |
| 9  | Ambiguous            | "How many calories should I eat to lose weight?" *(should be refused)* |
| 10 | Ambiguous            | "What supplement should I take for my iron deficiency?" *(should be refused)* |

### 10.2 Failure Detection Categories

| Failure Type        | Detection Method                                                     |
| ------------------- | -------------------------------------------------------------------- |
| Unbacked claims     | Manual review — claims stated as absolute fact without hedging       |
| Shifting numbers    | Run same question 3× and compare numeric values in responses         |
| Fake citations      | Check if `source` is non-null (schema violation for M1)              |
| Guardrail failures  | Q9/Q10 should be refused; flag if LLM answers substantively          |
| Hedged answers      | Manual review — responses that are so hedged they provide no value   |

### 10.3 Test Runner

```python
# backend/tests/failure_log.py

import asyncio
from app.services.llm_service import get_llm_response
from app.services.guardrails import check_guardrails
from app.models.database import FailureLog, get_session

TEST_QUESTIONS = [...]  # 10 questions from table above
RUNS_PER_QUESTION = 3

async def run_failure_tests():
    """Execute all test questions multiple times and record failures."""
    results = []
    for q in TEST_QUESTIONS:
        for run in range(1, RUNS_PER_QUESTION + 1):
            guardrail = check_guardrails(q["question"])
            if guardrail.blocked:
                response = {"answer": guardrail.reason, "claims": []}
            else:
                response = await get_llm_response(q["question"])

            # Record for manual + automated review
            results.append({
                "question_id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "response": response,
                "run_number": run,
            })
    return results
```

---

## 11. Environment & Configuration

```bash
# backend/.env.example

OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./nutrition.db
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=info
```

```python
# backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "sqlite:///./nutrition.db"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "info"

    class Config:
        env_file = ".env"
```

---

## 12. Deployment Architecture

```mermaid
flowchart LR
    subgraph Vercel["Vercel (Frontend)"]
        NJ["Next.js App"]
    end

    subgraph Railway["Railway (Backend)"]
        FA["FastAPI App"]
        SQL["SQLite File"]
    end

    subgraph OpenAI["OpenAI"]
        API["GPT-4o API"]
    end

    User -->|HTTPS| NJ
    NJ -->|API calls| FA
    FA -->|Structured Output| API
    FA -->|read/write| SQL
```

| Step | Action                                                   |
| ---- | -------------------------------------------------------- |
| 1    | Push code to **GitHub** repository                       |
| 2    | Connect **Vercel** to GitHub → auto-deploy `frontend/`   |
| 3    | Connect **Railway** to GitHub → auto-deploy `backend/`   |
| 4    | Set environment variables on both platforms              |
| 5    | Configure Vercel `NEXT_PUBLIC_API_URL` to Railway URL    |

---

## 13. M2 Extension Points

This architecture is designed with clear seams for Milestone 2's retrieval layer:

| Component            | M1 (Current)                | M2 (Planned)                                    |
| -------------------- | --------------------------- | ------------------------------------------------ |
| `claims[].source`    | Always `null`               | Populated with verified URLs/citations           |
| `SourcesPanel`       | Empty placeholder           | Displays linked sources per claim                |
| `llm_service.py`     | Direct LLM call             | RAG pipeline: retrieve → augment → generate      |
| `guardrails.py`      | Regex/pattern-based         | Optional ML-based intent classifier              |
| Database             | SQLite                      | Postgres/Supabase for production scale           |
| `failure_logs`       | Baseline recording          | Comparison against M1 baseline                   |
