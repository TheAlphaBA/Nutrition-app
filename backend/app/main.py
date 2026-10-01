"""
AI Nutrition Assistant — FastAPI Backend
========================================
Entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db
from app.routers.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: initialize database tables
    init_db()
    yield
    # Shutdown


# Create FastAPI app
app = FastAPI(
    title="AI Nutrition Assistant",
    description="An AI-powered chatbot that answers questions about food, nutrition, and food safety.",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS with Vercel regex pattern support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "environment": settings.environment}
