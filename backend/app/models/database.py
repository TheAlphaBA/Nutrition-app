"""
Database Models & Connection Configuration
==========================================
SQLAlchemy models for:
- Conversation: thread of messages
- Message: individual user/assistant chat messages
- Claim: extracted factual claims (source is null for M1)
- FailureLog: records hallucinations/inconsistencies during test runs
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Generator, Optional, List

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    create_engine,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    Session,
)

from app.config import settings

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, created_at={self.created_at})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, index=True)
    conversation_id = Column(
        String(64),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(16), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    claims = relationship(
        "Claim",
        back_populates="message",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conv_id={self.conversation_id})>"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(64), primary_key=True, index=True)
    message_id = Column(
        String(64),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    claim_text = Column(Text, nullable=False)
    source = Column(Text, nullable=True)  # Always null in Milestone 1

    message = relationship("Message", back_populates="claims")

    def __repr__(self) -> str:
        return f"<Claim(id={self.id}, msg_id={self.message_id}, source={self.source})>"


class FailureLog(Base):
    __tablename__ = "failure_logs"

    id = Column(String(64), primary_key=True, index=True)
    test_question_id = Column(Integer, nullable=True)
    category = Column(String(64), nullable=True)
    question = Column(Text, nullable=False)
    response_snapshot = Column(Text, nullable=False)
    failure_type = Column(String(64), nullable=False)  # e.g. "hallucination", "shifting_numbers", "vagueness"
    run_number = Column(Integer, default=1, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<FailureLog(id={self.id}, type={self.failure_type}, q_id={self.test_question_id})>"


# ---------------------------------------------------------
# Database Engine & Session Factory
# ---------------------------------------------------------

_engine = None
_SessionFactory = None


def get_engine(db_url: Optional[str] = None):
    """Get or create the SQLAlchemy engine."""
    global _engine
    url = db_url or settings.database_url
    if _engine is None or db_url is not None:
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(url, connect_args=connect_args)
    return _engine


def get_session_factory(engine=None):
    """Get or create the sessionmaker factory."""
    global _SessionFactory
    if _SessionFactory is None or engine is not None:
        target_engine = engine or get_engine()
        _SessionFactory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=target_engine,
        )
    return _SessionFactory


def _auto_seed_if_empty(session: Session) -> None:
    """Auto-load seed conversations if database is empty on deployment."""
    import json
    from pathlib import Path

    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent / "data" / "seed_conversations.json",
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "seed_conversations.json",
        Path("/app/data/seed_conversations.json"),
    ]

    seed_file = None
    for p in candidate_paths:
        if p.exists():
            seed_file = p
            break

    if not seed_file:
        return

    try:
        with open(seed_file, "r") as f:
            data = json.load(f)

        for conv_data in data.get("conversations", []):
            conv = Conversation(
                id=conv_data["id"],
                created_at=datetime.fromisoformat(conv_data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(conv_data["updated_at"].replace("Z", "+00:00")),
            )
            session.add(conv)

            for msg_data in conv_data.get("messages", []):
                msg = Message(
                    id=msg_data["id"],
                    conversation_id=conv.id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    created_at=datetime.fromisoformat(msg_data["created_at"].replace("Z", "+00:00")),
                )
                session.add(msg)

                for claim_data in msg_data.get("claims", []):
                    claim = Claim(
                        id=claim_data["id"],
                        message_id=msg.id,
                        claim_text=claim_data["text"],
                        source=None,
                    )
                    session.add(claim)

        session.commit()
    except Exception:
        session.rollback()


def init_db(engine=None) -> None:
    """Initialize all tables defined in Base and auto-seed if empty."""
    target_engine = engine or get_engine()
    Base.metadata.create_all(bind=target_engine)

    SessionFactory = get_session_factory(target_engine)
    session = SessionFactory()
    try:
        if session.query(Conversation).count() == 0:
            _auto_seed_if_empty(session)
    except Exception:
        pass
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request
    and guarantees proper closing/rollback on exception.
    """
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
