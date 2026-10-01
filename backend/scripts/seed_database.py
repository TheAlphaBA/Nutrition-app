"""
Seed Database Script
====================
Loads seed data from data/seed_conversations.json into the SQLite database.
Run this script during Phase 2 after the database models are created.

Usage:
    cd backend
    python -m scripts.seed_database

    Or from project root:
    python backend/scripts/seed_database.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path so we can import app modules
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Path to seed data
PROJECT_ROOT = BACKEND_DIR.parent
SEED_DATA_PATH = PROJECT_ROOT / "data" / "seed_conversations.json"


def parse_datetime(dt_string: str) -> datetime:
    """Parse ISO format datetime string."""
    return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))


def seed_database():
    """Load seed conversations into the database."""
    # These imports will work once Phase 2 models are created
    try:
        from app.models.database import (
            Base,
            Conversation,
            Message,
            Claim,
            get_engine,
            get_session_factory,
        )
    except ImportError:
        print("ERROR: Database models not yet created.")
        print("This script should be run after Phase 2 is complete.")
        print("Expected module: backend/app/models/database.py")
        sys.exit(1)

    # Load seed data
    if not SEED_DATA_PATH.exists():
        print(f"ERROR: Seed data file not found at {SEED_DATA_PATH}")
        sys.exit(1)

    with open(SEED_DATA_PATH, "r") as f:
        seed_data = json.load(f)

    # Create tables if they don't exist
    engine = get_engine()
    Base.metadata.create_all(engine)

    # Create session
    SessionFactory = get_session_factory(engine)
    session = SessionFactory()

    conversations_created = 0
    messages_created = 0
    claims_created = 0

    try:
        for conv_data in seed_data["conversations"]:
            # Check if conversation already exists
            existing = session.query(Conversation).filter_by(id=conv_data["id"]).first()
            if existing:
                print(f"  Skipping conversation {conv_data['id']} (already exists)")
                continue

            # Create conversation
            conversation = Conversation(
                id=conv_data["id"],
                created_at=parse_datetime(conv_data["created_at"]),
                updated_at=parse_datetime(conv_data["updated_at"]),
            )
            session.add(conversation)
            conversations_created += 1

            # Create messages and claims
            for msg_data in conv_data["messages"]:
                message = Message(
                    id=msg_data["id"],
                    conversation_id=conv_data["id"],
                    role=msg_data["role"],
                    content=msg_data["content"],
                    created_at=parse_datetime(msg_data["created_at"]),
                )
                session.add(message)
                messages_created += 1

                # Create claims for this message
                for claim_data in msg_data.get("claims", []):
                    claim = Claim(
                        id=claim_data["id"],
                        message_id=msg_data["id"],
                        claim_text=claim_data["text"],
                        source=claim_data["source"],  # Always null in M1
                    )
                    session.add(claim)
                    claims_created += 1

        session.commit()
        print(f"\n✅ Seed data loaded successfully!")
        print(f"   Conversations: {conversations_created}")
        print(f"   Messages:      {messages_created}")
        print(f"   Claims:        {claims_created}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


def verify_seed():
    """Verify the seeded data by printing summary counts."""
    try:
        from app.models.database import (
            Conversation,
            Message,
            Claim,
            get_engine,
            get_session_factory,
        )
    except ImportError:
        print("Cannot verify — models not yet available.")
        return

    engine = get_engine()
    SessionFactory = get_session_factory(engine)
    session = SessionFactory()

    try:
        conv_count = session.query(Conversation).count()
        msg_count = session.query(Message).count()
        claim_count = session.query(Claim).count()

        print(f"\n📊 Database Summary:")
        print(f"   Conversations: {conv_count}")
        print(f"   Messages:      {msg_count}")
        print(f"   Claims:        {claim_count}")

        # Print conversation previews
        print(f"\n📝 Conversations:")
        for conv in session.query(Conversation).all():
            msg_count = len(conv.messages)
            first_msg = conv.messages[0].content[:60] if conv.messages else "—"
            print(f"   [{conv.id}] {msg_count} messages — \"{first_msg}...\"")

    finally:
        session.close()


if __name__ == "__main__":
    print("🌱 Seeding database with sample data...")
    print(f"   Source: {SEED_DATA_PATH}")
    seed_database()
    verify_seed()
