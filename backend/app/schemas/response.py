"""
Response Schemas
================
Pydantic models for outgoing API responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ClaimSchema(BaseModel):
    """An individual factual claim extracted from an assistant response."""
    id: Optional[str] = None
    text: str = Field(..., description="The factual claim text.")
    source: Optional[str] = Field(
        default=None,
        description="Source citation for the claim. Always null in Milestone 1.",
    )


class ChatResponse(BaseModel):
    """Payload returned by POST /api/chat."""
    conversation_id: str
    message_id: str
    answer: str
    claims: List[ClaimSchema] = Field(default_factory=list)
    guardrail_triggered: bool = False
    guardrail_reason: Optional[str] = None


class MessageResponse(BaseModel):
    """Individual message in conversation history."""
    id: str
    role: str
    content: str
    created_at: datetime
    claims: List[ClaimSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Full conversation detail with all messages and claims."""
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationSummaryResponse(BaseModel):
    """Summary of a conversation for list views."""
    id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    preview: str

    class Config:
        from_attributes = True
