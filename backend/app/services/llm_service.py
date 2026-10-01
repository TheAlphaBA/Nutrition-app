"""
LLM Service
===========
Handles structured completions from Google Gemini or OpenAI.
Enforces the JSON response schema and Milestone 1 null-source requirement.
Includes a graceful offline fallback if no API key is yet configured.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from openai import OpenAI

from app.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Structured Output JSON Schema (as specified in architecture.md §5.3)
NUTRITION_RESPONSE_SCHEMA = {
    "name": "nutrition_response",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "The complete answer text in clear markdown",
            },
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "A single factual claim made in the answer",
                        },
                        "source": {
                            "type": ["string", "null"],
                            "description": "Source citation. Must be null for Milestone 1.",
                        },
                    },
                    "required": ["text", "source"],
                    "additionalProperties": False,
                },
                "description": "List of factual claims extracted from the answer",
            },
        },
        "required": ["answer", "claims"],
        "additionalProperties": False,
    },
}


def get_llm_client() -> tuple[Optional[OpenAI], str]:
    """
    Initializes the OpenAI-compatible client.
    Supports Google Gemini (via OpenAI compatibility endpoint) or native OpenAI.
    Returns (client, model_name).
    """
    gemini_key = settings.gemini_api_key.strip()
    openai_key = settings.openai_api_key.strip()

    # Priority 1: Gemini if key is provided or configured
    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return client, "gemini-1.5-flash"

    # Priority 2: OpenAI if key is provided
    if openai_key and openai_key != "sk-your-openai-api-key-here":
        client = OpenAI(api_key=openai_key)
        return client, "gpt-4o"

    # Fallback: No key configured yet
    return None, "mock-offline"


def format_conversation_history(messages: List[Any]) -> List[Dict[str, str]]:
    """
    Convert database Message objects into OpenAI/Gemini chat history dicts.
    """
    formatted = []
    for msg in messages:
        if hasattr(msg, "role") and hasattr(msg, "content"):
            formatted.append({"role": msg.role, "content": msg.content})
        elif isinstance(msg, dict):
            formatted.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    return formatted


def _generate_offline_mock_response(user_message: str) -> Dict[str, Any]:
    """
    Graceful offline mock when no API key is provided yet.
    Allows testing full frontend/backend flow out of the box.
    """
    cleaned = user_message.strip()
    return {
        "answer": (
            f"Here is nutrition information regarding **{cleaned}**:\n\n"
            "Whole foods provide essential micronutrients, vitamins, and minerals that support "
            "metabolic function, immune response, and overall vitality.\n\n"
            "*Note: The backend is currently running in local offline mode because no API key has been added yet.*"
        ),
        "claims": [
            {
                "text": f"Nutritional inquiry processed for: {cleaned}",
                "source": None,
            },
            {
                "text": "Whole food sources deliver bioavailable vitamins and minerals necessary for cellular health.",
                "source": None,
            },
            {
                "text": "Balanced dietary intake requires diverse nutrient sources across food groups.",
                "source": None,
            },
        ],
    }


async def get_llm_response(
    history: List[Dict[str, str]],
    user_message: str,
) -> Dict[str, Any]:
    """
    Execute structured LLM completion and enforce Milestone 1 null sources.
    """
    client, model_name = get_llm_client()

    if client is None:
        logger.warning("No Gemini or OpenAI API key found; returning mock response.")
        return _generate_offline_mock_response(user_message)

    # Build messages list starting with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": NUTRITION_RESPONSE_SCHEMA,
            },
            temperature=0.2,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

    except Exception as e:
        logger.error(f"Error calling LLM provider ({model_name}): {e}", exc_info=True)
        # Attempt fallback to basic JSON mode if json_schema is unsupported by the model version
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages + [
                    {
                        "role": "user",
                        "content": "Return ONLY valid JSON matching: {'answer': '...', 'claims': [{'text': '...', 'source': null}]}",
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
        except Exception as fallback_err:
            logger.error(f"Fallback JSON mode also failed: {fallback_err}")
            raise RuntimeError(f"LLM request failed: {e}") from e

    # Milestone 1 Enforcement: All claims MUST have source = None
    if "claims" in parsed and isinstance(parsed["claims"], list):
        for claim in parsed["claims"]:
            claim["source"] = None
    else:
        parsed["claims"] = []

    if "answer" not in parsed:
        parsed["answer"] = "No answer provided."

    return parsed
