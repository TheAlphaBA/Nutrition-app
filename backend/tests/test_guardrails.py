"""
Phase 4 Guardrails Unit Tests
=============================
Tests deterministic code-enforced guardrails against:
- 15 prohibited questions (calorie targets, body weight, medical advice)
- 15 safe nutrition questions
- Full API integration with POST /api/chat
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_session
from app.services.guardrails import (
    check_guardrails,
    GuardrailCategory,
    REFUSAL_MESSAGES,
)


class TestGuardrailsUnit(unittest.TestCase):
    """Test guardrail regex and classification in isolation against test dataset."""

    @classmethod
    def setUpClass(cls):
        test_file = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "guardrail_test_cases.json"
        )
        with open(test_file, "r") as f:
            cls.test_cases = json.load(f)["guardrail_test_cases"]

    def test_all_15_blocked_cases(self):
        """All 15 prohibited test queries MUST be blocked with the exact expected category."""
        for case in self.test_cases["must_block"]:
            query = case["input"]
            expected_cat = case["expected_category"]
            result = check_guardrails(query)

            self.assertTrue(
                result.blocked,
                f"Query should be blocked: '{query}' (ID: {case['id']})",
            )
            self.assertEqual(
                result.category.value if result.category else None,
                expected_cat,
                f"Incorrect category for '{query}' (ID: {case['id']})",
            )
            self.assertEqual(
                result.refusal_message,
                REFUSAL_MESSAGES[GuardrailCategory(expected_cat)],
            )

    def test_all_15_allowed_cases(self):
        """All 15 valid nutrition queries MUST pass through without being blocked."""
        for case in self.test_cases["must_allow"]:
            query = case["input"]
            result = check_guardrails(query)

            self.assertFalse(
                result.blocked,
                f"Safe query was erroneously blocked: '{query}' (ID: {case['id']})",
            )
            self.assertIsNone(result.category)
            self.assertIsNone(result.reason)


class TestGuardrailsApiIntegration(unittest.TestCase):
    """Test that POST /api/chat intercepts blocked queries before LLM invocation."""

    def setUp(self):
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

    def test_blocked_request_returns_refusal(self):
        """Sending a prohibited query returns refusal, no claims, and sets guardrail_triggered."""
        payload = {"message": "How many calories should I eat per day?"}
        res = self.client.post("/api/chat", json=payload)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["guardrail_triggered"])
        self.assertEqual(data["guardrail_reason"], "calorie_weight_target")
        self.assertEqual(data["claims"], [])
        self.assertIn("unable to provide specific calorie", data["answer"])

    def test_medical_advice_blocked(self):
        """Medical advice query is blocked immediately."""
        payload = {"message": "What medication helps with high cholesterol?"}
        res = self.client.post("/api/chat", json=payload)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["guardrail_triggered"])
        self.assertEqual(data["guardrail_reason"], "medical_advice")
        self.assertEqual(data["claims"], [])

    def test_safe_request_passes_guardrail(self):
        """Safe nutrition questions pass through with guardrail_triggered=False."""
        payload = {"message": "How many calories are in a banana?"}
        res = self.client.post("/api/chat", json=payload)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["guardrail_triggered"])
        self.assertIsNone(data["guardrail_reason"])
        self.assertIsInstance(data["claims"], list)


if __name__ == "__main__":
    unittest.main()
