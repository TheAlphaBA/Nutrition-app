"""
Chat Router
===========
API endpoints for:
- POST /api/chat: send a message and receive structured answer with claims
- POST /api/conversations: create a new conversation thread
- GET  /api/conversations: list recent conversations
- GET  /api/conversations/{id}: get conversation history with claims
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import Conversation, Message, Claim, get_session
from app.schemas.request import ChatRequest, CreateConversationRequest
from app.schemas.response import (
    ChatResponse,
    ClaimSchema,
    ConversationDetailResponse,
    ConversationSummaryResponse,
    MessageResponse,
)
from app.services.llm_service import (
    get_llm_response,
    format_conversation_history,
)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/conversations", status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: Optional[CreateConversationRequest] = None,
    db: Session = Depends(get_session),
):
    """Create a new conversation."""
    conv_id = (payload and payload.id) or f"conv-{uuid.uuid4().hex[:12]}"
    existing = db.query(Conversation).filter_by(id=conv_id).first()
    if existing:
        return {"id": existing.id, "created_at": existing.created_at}

    now = datetime.utcnow()
    conv = Conversation(id=conv_id, created_at=now, updated_at=now)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "created_at": conv.created_at}


@router.get("/conversations", response_model=List[ConversationSummaryResponse])
def list_conversations(
    limit: int = 50,
    db: Session = Depends(get_session),
):
    """List recent conversations with message counts and previews."""
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .all()
    )

    summaries = []
    for conv in conversations:
        msg_count = len(conv.messages)
        preview = conv.messages[0].content[:80] if conv.messages else "New conversation"
        summaries.append(
            ConversationSummaryResponse(
                id=conv.id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count,
                preview=preview,
            )
        )
    return summaries


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_session),
):
    """Retrieve full conversation history including messages and claims."""
    conv = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found.",
        )

    formatted_messages = []
    for msg in conv.messages:
        formatted_claims = [
            ClaimSchema(id=c.id, text=c.claim_text, source=c.source)
            for c in msg.claims
        ]
        formatted_messages.append(
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                claims=formatted_claims,
            )
        )

    return ConversationDetailResponse(
        id=conv.id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_session),
):
    """
    Primary chat endpoint.
    Processes user nutrition question, queries LLM, persists conversation,
    and returns answer with extracted claims.
    """
    user_query = request.message.strip()
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty.",
        )

    # 1. Retrieve or create conversation
    now = datetime.utcnow()
    if request.conversation_id:
        conv = db.query(Conversation).filter_by(id=request.conversation_id).first()
        if not conv:
            conv = Conversation(id=request.conversation_id, created_at=now, updated_at=now)
            db.add(conv)
            db.flush()
    else:
        conv_id = f"conv-{uuid.uuid4().hex[:12]}"
        conv = Conversation(id=conv_id, created_at=now, updated_at=now)
        db.add(conv)
        db.flush()

    # 2. Persist user message
    user_msg_id = f"msg-{uuid.uuid4().hex[:12]}"
    user_msg = Message(
        id=user_msg_id,
        conversation_id=conv.id,
        role="user",
        content=user_query,
        created_at=now,
    )
    db.add(user_msg)
    db.flush()

    # 3. Format conversation history for context
    history = format_conversation_history(conv.messages[:-1])

    # 4. Generate structured LLM response
    llm_output = await get_llm_response(history=history, user_message=user_query)

    answer_text = llm_output.get("answer", "")
    raw_claims = llm_output.get("claims", [])

    # 5. Persist assistant response
    asst_msg_id = f"msg-{uuid.uuid4().hex[:12]}"
    asst_msg = Message(
        id=asst_msg_id,
        conversation_id=conv.id,
        role="assistant",
        content=answer_text,
        created_at=datetime.utcnow(),
    )
    db.add(asst_msg)
    db.flush()

    # 6. Persist claims (enforcing source is None for M1)
    response_claims: List[ClaimSchema] = []
    for c in raw_claims:
        claim_text = c.get("text", "").strip() if isinstance(c, dict) else str(c).strip()
        if not claim_text:
            continue
        claim_id = f"claim-{uuid.uuid4().hex[:12]}"
        claim_obj = Claim(
            id=claim_id,
            message_id=asst_msg.id,
            claim_text=claim_text,
            source=None,  # Hardcoded None for Milestone 1
        )
        db.add(claim_obj)
        response_claims.append(
            ClaimSchema(id=claim_id, text=claim_text, source=None)
        )

    # 7. Update conversation timestamp and commit
    conv.updated_at = datetime.utcnow()
    db.commit()

    return ChatResponse(
        conversation_id=conv.id,
        message_id=asst_msg.id,
        answer=answer_text,
        claims=response_claims,
        guardrail_triggered=False,
        guardrail_reason=None,
    )
