"""
Guardrails Engine (Code-Enforced)
=================================
Pre-processing filter that intercepts blocked queries before they reach the LLM:
1. Calorie / weight targets
2. Body weight recommendations / BMI advice
3. Medical advice / prescription / diagnosis queries

Enforced via deterministic regex matching and keyword heuristics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class GuardrailCategory(str, Enum):
    CALORIE_WEIGHT_TARGET = "calorie_weight_target"
    BODY_WEIGHT_RECOMMENDATION = "body_weight_recommendation"
    MEDICAL_ADVICE = "medical_advice"


@dataclass
class GuardrailResult:
    blocked: bool
    category: Optional[GuardrailCategory] = None
    reason: Optional[str] = None
    refusal_message: Optional[str] = None


REFUSAL_MESSAGES: Dict[GuardrailCategory, str] = {
    GuardrailCategory.CALORIE_WEIGHT_TARGET: (
        "I am unable to provide specific calorie or daily caloric intake targets. "
        "Calorie requirements depend heavily on individual factors including age, sex, metabolic health, "
        "and physical activity levels. Please consult a registered dietitian or healthcare professional "
        "for a personalized assessment."
    ),
    GuardrailCategory.BODY_WEIGHT_RECOMMENDATION: (
        "I am unable to recommend what a person should weigh or provide weight loss diet plans. "
        "A healthy weight range varies significantly from person to person based on body composition, "
        "medical history, and individual physiology. Please consult a qualified healthcare provider "
        "for personalized guidance."
    ),
    GuardrailCategory.MEDICAL_ADVICE: (
        "I am unable to provide medical advice, diagnoses, drug recommendations, or treatment plans for health conditions. "
        "NutriBot provides general food and nutrition information only. If you have questions regarding medical conditions, "
        "deficiencies, supplements, or medications, please consult a licensed physician or medical professional."
    ),
}

PATTERNS: Dict[GuardrailCategory, List[str]] = {
    GuardrailCategory.CALORIE_WEIGHT_TARGET: [
        r"how many calories (should|do|can|must|to) (i|we|one|a person)?\s*(eat|consume|need|have)",
        r"(daily|my|what'?s my daily) calor(ie|ic) (intake|target|goal|budget|limit|requirement)",
        r"how many calories .*to (lose|gain|maintain) weight",
        r"how many calories should (we|i) consume",
    ],
    GuardrailCategory.BODY_WEIGHT_RECOMMENDATION: [
        r"(ideal|healthy|target|goal) weight for",
        r"how much should (i|a person|we|one) weigh",
        r"what should (i|my) (weight|bmi) be",
        r"what is (the|my) (ideal|healthy|target) (weight|bmi)",
        r"weight loss .*(plan|diet|program)",
    ],
    GuardrailCategory.MEDICAL_ADVICE: [
        r"should i take .*supplement.*for",
        r"what medication (helps|works|is good|should i take)",
        r"prescribe (something|a drug|medicine|medication) for",
        r"(treat|cure|remedy) (my|the) .*(deficiency|disease|illness|condition|pain|infection)",
        r"how do i treat my",
        r"diagnose (my|these)? .*symptoms",
        r"what drug should (i|we) (use|take)",
    ],
}


def check_guardrails(text: str) -> GuardrailResult:
    """
    Evaluate user input against code-enforced guardrail rules.
    Returns GuardrailResult with blocked=True if any prohibited pattern matches.
    """
    if not text:
        return GuardrailResult(blocked=False)

    # Normalize whitespace and lowercase
    normalized = re.sub(r"\s+", " ", text.lower().strip())

    for category, pattern_list in PATTERNS.items():
        for pattern in pattern_list:
            if re.search(pattern, normalized):
                return GuardrailResult(
                    blocked=True,
                    category=category,
                    reason=category.value,
                    refusal_message=REFUSAL_MESSAGES[category],
                )

    return GuardrailResult(blocked=False)
