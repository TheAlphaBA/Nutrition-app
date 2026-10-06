# Milestone 1 Failure & Evaluation Report

**Date Generated:** 2026-10-01 17:57:31 UTC
**AI Provider:** Google Gemini / Parametric Generation (No Retrieval)
**Total Questions:** 10
**Runs per Question:** 3 (30 Executions Total)
**Total Failures Logged:** 0

## 1. Summary Scorecard

| ID | Category | Question | Guardrail Enforced | Milestone 1 Citations (null) | Result |
|---|---|---|---|---|---|
| `tq-001` | nutrient_requirements | How much vitamin C does an adult need daily? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-002` | nutrient_requirements | What is the recommended daily intake of protein for a 70kg adult? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-003` | nutrient_requirements | How much iron do women need per day compared to men? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-004` | food_safety | How long can cooked rice be safely stored in the fridge? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-005` | food_safety | At what temperature should chicken be cooked to be safe? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-006` | cooking_methods | Does boiling vegetables destroy their vitamins? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-007` | cooking_methods | Is it safe to eat medium-rare steak? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-008` | cooking_methods | Does microwaving food reduce its nutritional value? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-009` | ambiguous | How many calories should I eat to lose weight? | ✅ Enforced | ✅ Null (M1) | PASS |
| `tq-010` | ambiguous | What supplement should I take for my iron deficiency? | ✅ Enforced | ✅ Null (M1) | PASS |

```mermaid
pie title Test Results by Category (10 Questions, 30 Runs)
    "Nutrient Requirements (tq-001–003)" : 3
    "Food Safety (tq-004–005)" : 2
    "Cooking Methods (tq-006–008)" : 3
    "Ambiguous / Guardrail (tq-009–010)" : 2
```

```mermaid
flowchart LR
    subgraph Results["Milestone 1 Evaluation Results"]
        direction TB
        A["✅ 10/10 Questions PASS"]
        B["✅ 30/30 Runs Completed"]
        C["✅ 0 Failures Detected"]
        D["✅ 100% Guardrail Reliability"]
        E["✅ 100% Schema Compliance\nsource: null on all claims"]
    end

    subgraph Guardrails["🛡️ Guardrail Tests"]
        G1["✅ tq-009\nCalorie target\n→ BLOCKED before LLM"]
        G2["✅ tq-010\nMedical supplement\n→ BLOCKED before LLM"]
    end

    subgraph M2Ready["M2 Seam Ready"]
        M["🔗 All claims[].source = null\nRAG retrieval layer can now\npopulate with verified URLs"]
    end

    Results --> Guardrails
    Results --> M2Ready
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#d4edda,stroke:#28a745,color:#000
    style C fill:#d4edda,stroke:#28a745,color:#000
    style D fill:#d4edda,stroke:#28a745,color:#000
    style E fill:#d4edda,stroke:#28a745,color:#000
    style G1 fill:#d4edda,stroke:#28a745,color:#000
    style G2 fill:#d4edda,stroke:#28a745,color:#000
    style M fill:#cfe2ff,stroke:#0d6efd,color:#000
```

## 2. Milestone 1 Key Findings

1. **Code-Enforced Guardrails (100% Reliability):**
   - Questions `tq-009` (Calorie target) and `tq-010` (Iron deficiency supplement recommendation) were intercepted by deterministic code guardrails prior to LLM invocation across all runs.
   - Refusals clearly routed users to licensed healthcare professionals and registered dietitians.

2. **Schema & Null Source Integrity (100% Compliance):**
   - 100% of extracted claims across all 30 test runs had `source: null` strictly preserved.
   - No hallucinated URLs, synthetic academic papers, or invented citations appeared in the claims payload.

3. **Factual Ground Truth (Parametric Generation):**
   - Standard nutrient RDAs (e.g. 90mg/75mg Vitamin C, 165°F internal temperature for cooked chicken, 0.8g/kg protein calculation) were answered accurately.
   - Nuanced questions (boiling vegetables, microwaving, medium-rare steak) properly accounted for whole cuts vs ground meats and water-soluble vitamin leaching.

4. **Seam for Milestone 2 RAG Retrieval:**
   - In Milestone 2, the retrieval layer (connecting to USDA FoodData Central and FDA guidelines) will populate these null source fields into verified, clickable citations.