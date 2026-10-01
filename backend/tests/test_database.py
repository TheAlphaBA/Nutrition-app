"""
Phase 2 Database & Models Unit Tests
====================================
Tests the database models, relationships, session handling, and schema creation.
Uses standard Python unittest against an in-memory SQLite database.
"""

from __future__ import annotations

import unittest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.models.database import (
    Base,
    Conversation,
    Message,
    Claim,
    FailureLog,
    get_session_factory,
    get_session,
    init_db,
)


class TestDatabaseModels(unittest.TestCase):
    def setUp(self):
        """Set up an in-memory SQLite database for testing."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.session = self.SessionFactory()

    def tearDown(self):
        """Clean up the test database session and drop all tables."""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_tables_created(self):
        """Task 2.1: Verify all 4 required tables are created in the database schema."""
        inspector = inspect(self.engine)
        tables = set(inspector.get_table_names())
        expected_tables = {"conversations", "messages", "claims", "failure_logs"}
        self.assertTrue(
            expected_tables.issubset(tables),
            f"Missing expected tables. Found: {tables}",
        )

    def test_conversation_crud(self):
        """Task 2.2: Test Conversation model creation, insertion, and retrieval."""
        conv = Conversation(id="conv-test-01")
        self.session.add(conv)
        self.session.commit()

        retrieved = self.session.query(Conversation).filter_by(id="conv-test-01").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "conv-test-01")
        self.assertIsInstance(retrieved.created_at, datetime)

    def test_message_relationship(self):
        """Task 2.3: Test Message model linked via foreign key to Conversation."""
        conv = Conversation(id="conv-test-02")
        self.session.add(conv)
        self.session.commit()

        msg1 = Message(
            id="msg-test-01",
            conversation_id="conv-test-02",
            role="user",
            content="Is spinach high in iron?",
        )
        msg2 = Message(
            id="msg-test-02",
            conversation_id="conv-test-02",
            role="assistant",
            content="Yes, 100g of raw spinach contains approximately 2.7 mg of iron.",
        )
        self.session.add_all([msg1, msg2])
        self.session.commit()

        retrieved_conv = self.session.query(Conversation).filter_by(id="conv-test-02").first()
        self.assertEqual(len(retrieved_conv.messages), 2)
        self.assertEqual(retrieved_conv.messages[0].role, "user")
        self.assertEqual(retrieved_conv.messages[1].role, "assistant")

    def test_claim_model_and_null_source(self):
        """Task 2.4: Test Claim model linked to Message with nullable source (null in M1)."""
        conv = Conversation(id="conv-test-03")
        self.session.add(conv)
        self.session.commit()

        msg = Message(
            id="msg-test-03",
            conversation_id="conv-test-03",
            role="assistant",
            content="100g of raw spinach contains 2.7 mg of iron.",
        )
        self.session.add(msg)
        self.session.commit()

        claim = Claim(
            id="claim-test-01",
            message_id="msg-test-03",
            claim_text="100g raw spinach contains ~2.7 mg iron",
            source=None,  # Nullable in M1
        )
        self.session.add(claim)
        self.session.commit()

        retrieved_msg = self.session.query(Message).filter_by(id="msg-test-03").first()
        self.assertEqual(len(retrieved_msg.claims), 1)
        self.assertEqual(retrieved_msg.claims[0].claim_text, "100g raw spinach contains ~2.7 mg iron")
        self.assertIsNone(retrieved_msg.claims[0].source)

    def test_failure_log_model(self):
        """Task 2.5: Test FailureLog model insertion and querying."""
        log = FailureLog(
            id="fail-test-01",
            test_question_id=1,
            category="factual_recall",
            question="How much iron is in 100g of raw spinach?",
            response_snapshot="100g spinach has 15mg of iron.",
            failure_type="hallucination",
            run_number=1,
        )
        self.session.add(log)
        self.session.commit()

        retrieved_log = self.session.query(FailureLog).filter_by(id="fail-test-01").first()
        self.assertIsNotNone(retrieved_log)
        self.assertEqual(retrieved_log.failure_type, "hallucination")
        self.assertEqual(retrieved_log.test_question_id, 1)

    def test_cascade_delete(self):
        """Verify cascade deletion from Conversation down to Messages and Claims."""
        conv = Conversation(id="conv-cascade-01")
        self.session.add(conv)
        self.session.commit()

        msg = Message(
            id="msg-cascade-01",
            conversation_id="conv-cascade-01",
            role="assistant",
            content="Test message",
        )
        self.session.add(msg)
        self.session.commit()

        claim = Claim(
            id="claim-cascade-01",
            message_id="msg-cascade-01",
            claim_text="Test claim",
            source=None,
        )
        self.session.add(claim)
        self.session.commit()

        # Delete conversation
        self.session.delete(conv)
        self.session.commit()

        # Verify message and claim were cascade deleted
        self.assertIsNone(self.session.query(Message).filter_by(id="msg-cascade-01").first())
        self.assertIsNone(self.session.query(Claim).filter_by(id="claim-cascade-01").first())

    def test_get_session_dependency(self):
        """Task 2.6: Test get_session generator yields a functional session."""
        session_gen = get_session()
        db_session = next(session_gen)
        self.assertIsNotNone(db_session)
        # Ensure it works for queries
        try:
            res = db_session.query(Conversation).all()
            self.assertIsInstance(res, list)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass


if __name__ == "__main__":
    unittest.main()
