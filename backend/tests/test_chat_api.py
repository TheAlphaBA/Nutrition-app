"""
Phase 3 Backend Core & API Tests
================================
Tests the chat endpoints, conversation retrieval, persistence,
and structured output null-source enforcement.
"""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_session
from app.prompts.system_prompt import SYSTEM_PROMPT


class TestChatEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up in-memory DB and FastAPI test client."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionFactory = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        def override_get_session():
            session = self.SessionFactory()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_session] = override_get_session
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(self.engine)

    def test_system_prompt_rules(self):
        """Verify system prompt contains all required instructions and boundaries."""
        self.assertIn("NutriBot", SYSTEM_PROMPT)
        self.assertIn("NOT a doctor", SYSTEM_PROMPT)
        self.assertIn("calorie targets", SYSTEM_PROMPT)
        self.assertIn("recommend what a person should weigh", SYSTEM_PROMPT)
        self.assertIn("medical advice", SYSTEM_PROMPT)
        self.assertIn("claims", SYSTEM_PROMPT)
        self.assertIn("null", SYSTEM_PROMPT)

    def test_post_chat_new_conversation(self):
        """Task 3C.1: Test POST /api/chat creates conversation, returns claims with null source."""
        payload = {"message": "What are the health benefits of spinach?"}
        response = self.client.post("/api/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("conversation_id", data)
        self.assertIn("message_id", data)
        self.assertTrue(data["answer"])
        self.assertIsInstance(data["claims"], list)
        self.assertFalse(data["guardrail_triggered"])

        # Enforce Milestone 1 requirement: all claims MUST have source=None
        for claim in data["claims"]:
            self.assertIn("text", claim)
            self.assertIsNone(claim["source"])

    def test_multi_turn_conversation(self):
        """Test multi-turn messages within the same conversation thread."""
        # Turn 1
        res1 = self.client.post(
            "/api/chat", json={"message": "What is vitamin C?"}
        )
        self.assertEqual(res1.status_code, 200)
        conv_id = res1.json()["conversation_id"]

        # Turn 2 using same conversation_id
        res2 = self.client.post(
            "/api/chat",
            json={"conversation_id": conv_id, "message": "Which fruits have the most?"},
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["conversation_id"], conv_id)

        # Retrieve conversation history
        detail_res = self.client.get(f"/api/conversations/{conv_id}")
        self.assertEqual(detail_res.status_code, 200)
        detail = detail_res.json()

        self.assertEqual(detail["id"], conv_id)
        # Should have 4 messages: user1, asst1, user2, asst2
        self.assertEqual(len(detail["messages"]), 4)
        self.assertEqual(detail["messages"][0]["role"], "user")
        self.assertEqual(detail["messages"][1]["role"], "assistant")
        self.assertEqual(detail["messages"][2]["role"], "user")
        self.assertEqual(detail["messages"][3]["role"], "assistant")

    def test_get_conversation_not_found(self):
        """Test GET /api/conversations/{id} with unknown ID returns 404."""
        res = self.client.get("/api/conversations/non-existent-conv")
        self.assertEqual(res.status_code, 404)

    def test_list_conversations(self):
        """Test GET /api/conversations returns list of recent threads."""
        self.client.post("/api/chat", json={"message": "Query 1"})
        self.client.post("/api/chat", json={"message": "Query 2"})

        res = self.client.get("/api/conversations")
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertGreaterEqual(len(items), 2)
        self.assertIn("message_count", items[0])
        self.assertIn("preview", items[0])

    def test_empty_message_validation(self):
        """Test POST /api/chat rejects empty message strings."""
        res = self.client.post("/api/chat", json={"message": "   "})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
