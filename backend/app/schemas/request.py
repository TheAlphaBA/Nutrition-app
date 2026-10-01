"""
Request Schemas
===============
Pydantic models for incoming API requests.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload for POST /api/chat."""
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID. If omitted, a new conversation is created.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's nutrition or food safety question.",
    )


class CreateConversationRequest(BaseModel):
    """Optional payload for POST /api/conversations."""
    id: Optional[str] = Field(
        default=None,
        description="Optional custom UUID for conversation ID.",
    )
