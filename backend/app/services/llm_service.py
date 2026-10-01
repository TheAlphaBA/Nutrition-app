"""
LLM Service
===========
Handles structured completions from Google Gemini (native REST) or OpenAI.
Enforces the JSON response schema and Milestone 1 null-source requirement.
Includes a graceful offline fallback if no API key is configured.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
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


def format_conversation_history(messages: List[Any]) -> List[Dict[str, str]]:
    """
    Convert database Message objects into chat history dicts.
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
    Graceful offline mock when no API key is provided.
    Allows testing full frontend/backend flow out of the box.
    """
    cleaned = user_message.strip()
    return {
        "answer": (
            f"Here is nutrition information regarding **{cleaned}**:\n\n"
            "Whole foods provide essential micronutrients, vitamins, and minerals that support "
            "metabolic function, immune response, and overall vitality.\n\n"
            "*Note: The backend is currently running in local offline mode.*"
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


def _sync_post_gemini(contents: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    """Execute synchronous HTTP request to Gemini API with model fallback."""
    candidate_models = ["gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]
    last_error = None

    with httpx.Client(timeout=25.0) as client:
        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": contents,
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2,
                },
            }
            try:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(raw_text)
                logger.warning(f"Model {model} returned status {response.status_code}: {response.text[:120]}")
                last_error = RuntimeError(f"{model} returned {response.status_code}")
            except Exception as e:
                logger.warning(f"Error querying {model}: {e}")
                last_error = e

    raise last_error or RuntimeError("All Gemini models failed")


async def _call_gemini(history: List[Dict[str, str]], user_message: str, api_key: str) -> Dict[str, Any]:
    """Call Google Gemini generateContent API with JSON response format using background thread."""
    import anyio

    # Build Gemini conversation contents
    contents: List[Dict[str, Any]] = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {
            "role": "model",
            "parts": [
                {
                    "text": (
                        "Understood. I am NutriBot. I will output strictly valid JSON matching the schema "
                        'with "answer" and "claims", setting "source": null for all claims.'
                    )
                }
            ],
        },
    ]

    for item in history:
        gemini_role = "model" if item["role"] == "assistant" else "user"
        contents.append({"role": gemini_role, "parts": [{"text": item["content"]}]})

    contents.append({"role": "user", "parts": [{"text": user_message}]})

    return await anyio.to_thread.run_sync(_sync_post_gemini, contents, api_key)


async def _call_openai(history: List[Dict[str, str]], user_message: str, api_key: str) -> Dict[str, Any]:
    """Call OpenAI Chat Completions API with structured output schema."""
    client = OpenAI(api_key=api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": NUTRITION_RESPONSE_SCHEMA,
        },
        temperature=0.2,
    )
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)


async def get_llm_response(
    history: List[Dict[str, str]],
    user_message: str,
) -> Dict[str, Any]:
    """
    Execute structured LLM completion and enforce Milestone 1 null sources.
    Priority:
    1. Gemini API if GEMINI_API_KEY is present
    2. OpenAI API if OPENAI_API_KEY is present
    3. Offline mock if neither key is set
    """
    gemini_key = settings.gemini_api_key.strip()
    openai_key = settings.openai_api_key.strip()

    parsed: Dict[str, Any]

    if gemini_key:
        try:
            parsed = await _call_gemini(history, user_message, gemini_key)
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            if openai_key and openai_key != "sk-your-openai-api-key-here":
                logger.info("Falling back to OpenAI...")
                parsed = await _call_openai(history, user_message, openai_key)
            else:
                logger.warning("Returning offline fallback due to Gemini error.")
                parsed = _generate_offline_mock_response(user_message)
    elif openai_key and openai_key != "sk-your-openai-api-key-here":
        try:
            parsed = await _call_openai(history, user_message, openai_key)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            parsed = _generate_offline_mock_response(user_message)
    else:
        logger.info("No API key configured; using offline mock.")
        parsed = _generate_offline_mock_response(user_message)

    # Milestone 1 Hard Enforcement: All claims MUST have source = None
    if "claims" in parsed and isinstance(parsed["claims"], list):
        for claim in parsed["claims"]:
            claim["source"] = None
    else:
        parsed["claims"] = []

    if "answer" not in parsed:
        parsed["answer"] = "No answer provided."

    return parsed
