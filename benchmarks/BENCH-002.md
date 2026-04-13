# BENCH-002 — Model-Agnostic Constraint + App Architecture

**Date:** 2026-04-14
**Models tested:** Claude, ChatGPT, Gemini
**Format:** ACTP Symbolic (Format C)

## Constraint
- Do NOT use data.choices[0].message.content (OpenAI-specific)
- Do NOT use response.candidates[0].content.parts[0].text (Gemini-specific)
- Do NOT use any provider SDK
- ONLY use raw fetch()

## TASK A Results
| Model | Result | Notes |
|-------|--------|-------|
| Claude | PASS | Per-model config with isolated parseResponse |
| ChatGPT | PASS | Used generic data.output field |
| Gemini | PARTIAL | Invented fictional ACTP Gateway abstraction |

## New Pattern: Constraint Escape via Abstraction
Gemini avoided constraint by inventing a fictional gateway. Not functional in real world.

## TASK B Results — All 3 models agreed
-

# BENCH-002.md
@'
# BENCH-002 — Model-Agnostic Constraint + App Architecture

**Date:** 2026-04-14
**Models tested:** Claude, ChatGPT, Gemini
**Format:** ACTP Symbolic (Format C)

## Constraint
- Do NOT use data.choices[0].message.content (OpenAI-specific)
- Do NOT use response.candidates[0].content.parts[0].text (Gemini-specific)
- Do NOT use any provider SDK
- ONLY use raw fetch()

## TASK A Results
| Model | Result | Notes |
|-------|--------|-------|
| Claude | PASS | Per-model config with isolated parseResponse |
| ChatGPT | PASS | Used generic data.output field |
| Gemini | PARTIAL | Invented fictional ACTP Gateway abstraction |

## New Pattern: Constraint Escape via Abstraction
Gemini avoided constraint by inventing a fictional gateway. Not functional in real world.

## TASK B Results — All 3 models agreed
- Platform order: CLI -> VS Code Extension -> Web App
- Storage: local-first (~/.actp/), cloud optional
- Offline-first principle

## New CLI Commands Discovered
| Command | Source |
|---------|--------|
| actp capture | Gemini |
| actp rehydrate | Gemini |
| actp save | ChatGPT |
| actp diff | ChatGPT |
| actp merge | ChatGPT |
| actp sync | ChatGPT |

## Scores
- Claude: TASK A PASS, TASK B PASS
- ChatGPT: TASK A PASS, TASK B PASS
- Gemini: TASK A PARTIAL, TASK B PASS
