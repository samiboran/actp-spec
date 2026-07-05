# ACTP — AI Context Transfer Protocol

> *"Don't explain your project again. Just transfer it."*

An open standard for exporting, importing, and transferring AI project context across different language models — Claude, ChatGPT, Gemini, and beyond.

---

## The Problem

Every time you switch AI models or start a new session, context is lost. Developers and AI power users waste significant time re-explaining projects, decisions, constraints, and current state.

There is no universal standard for AI-to-AI context transfer. ACTP is that standard.

---

## The Solution

ACTP defines a portable `.actp.json` format that captures the full **semantic state** of an AI-assisted project — decisions made, current code state, open questions, symbolic priority markers — in a model-agnostic, human-readable way.

Think of it as **Git for AI memory** — versioned, portable, owned by you.

---

## Core Principles

| Principle | Description |
|---|---|
| **Model-agnostic** | Works with Claude, ChatGPT, Gemini, or any future model |
| **User-owned** | No cloud dependency. Your data lives where you put it |
| **Semantic, not raw** | Captures decisions and state, not raw conversation transcripts |
| **Dual-layer encoding** | Machine-readable structured fields + human-readable symbolic markers |
| **Delta sync** | Only meaningful changes propagate — not full packet every time |

---

## Format Spec (v0.1)

```json
{
  "@context": "https://actp.dev/schema/v0.1",
  "@type": "ACTPPacket",
  "actp_version": "0.1",
  "created_at": "ISO8601",
  "vocabulary_hash": "actp-legend-v0.1",

  "symbol_legend": {
    "🔴": "priority=P0, mutability=LOCKED, certainty=HIGH",
    "🟡": "priority=P1, mutability=FLEXIBLE, certainty=MEDIUM",
    "🔵": "priority=P2, mutability=FLEXIBLE, certainty=LOW",
    "🟢": "status=COMPLETED",
    "🌫️": "certainty=LOW, hallucination_risk=true",
    "🔗": "external_dependency=true"
  },

  "project": {
    "name": "string",
    "goal": "One sentence description of the project's purpose",
    "constraints": ["🔴 immutable constraints — never change"],
    "soft_preferences": ["🟡 flexible preferences"]
  },

  "decisions": [
    {
      "id": "D1",
      "symbol": "🔴",
      "priority": "P0",
      "certainty": "HIGH",
      "mutability": "LOCKED",
      "content": "The decision made",
      "rationale": "Why this decision was made"
    }
  ],

  "tasks": [
    {
      "id": "T1",
      "status": "done | pending | blocked",
      "description": "string"
    }
  ],

  "artifacts": {
    "code_snippets": [
      { "id": "C1", "lang": "string", "content": "string" }
    ],
    "references": ["url or filename"]
  },

  "entity_map": {
    "ComponentName": "canonical identifier to prevent naming drift"
  },

  "priority_matrix": [
    { "segment": "decisions", "weight": 1.0 },
    { "segment": "tasks", "weight": 0.8 }
  ],

  "open_questions": ["string"],

  "next_steps": ["string"],

  "integrity_hash": "sha256 of content fields"
}
```

---

## Symbolic Layer

ACTP uses a two-layer encoding system inspired by human mnemonic techniques (Method of Loci, von Restorff Effect):

**Layer 1 — Structured fields (machine-readable, primary)**
```json
"priority": "P0",
"certainty": "HIGH",
"mutability": "LOCKED"
```

**Layer 2 — Symbolic markers (human-readable, secondary)**
```json
"symbol": "🔴"
```

Symbols are not decorative. High-entropy tokens like 🔴 increase attention weight in transformer models (von Restorff Effect), effectively pre-weighting the associated content. Symbols are always backed by structured fields — never standalone.

### Special Symbols

| Symbol | Meaning |
|---|---|
| 🌫️ | Hallucination risk — AI generated this with low certainty, verify before trusting |
| 🔗 | External dependency — relies on file, API, or doc not present in this packet |

---

## Node Architecture (ACTP-N)

ACTP defines two separate specs:

- **ACTP** — Data layer. What is carried (packet format, schema, compression).
- **ACTP-N** — Network layer. How packets move between nodes.

### Node Types

| Node | Role |
|---|---|
| **Local Node** | Creates and consumes packets (Claude, ChatGPT, Gemini instances) |
| **Relay Node** | MCP-based transport — filters and forwards deltas |
| **Snapshot Node** | Compressed stable state — rehydration checkpoint |
| **Refutation Node ⚔️** | Detects conflicts, prevents split-brain context drift |

### Sync Model

Sync is **event-driven**, not continuous. Triggers:
- Session end
- Major decision made
- Manual export
- Scheduled snapshot

Only **deltas propagate** — not the full packet every time.

### Propagation Rules

**Propagate:**
- Apex/goal changes
- 🔴 tag updates
- New artifacts
- Task state transitions
- Conflict introduction

**Suppress:**
- Minor wording changes
- Redundant summaries
- P2 updates (unless explicitly flagged)
- TTL-expired packets

### Conflict Resolution

Inspired by Git branching:

1. Conflicting decisions → **branch-both** (preserve both versions)
2. **Vector clocks** track causal ordering
3. P0 tie → **human-in-the-loop required** — no silent auto-merge ever
4. Un-rehydratable packets → **quarantined as dead letter context**, not discarded

---

## MCP Integration

ACTP is designed to work alongside [Model Context Protocol (MCP)](https://modelcontextprotocol.io):

```
MCP  = transport layer  →  which road to take
ACTP = payload layer    →  what to carry
```

ACTP-N nodes can be implemented as MCP extensions, leveraging the existing MCP ecosystem for transport while adding the ACTP context payload standard on top.

---

## How to Use

### Manual (current)
1. At session end, generate an ACTP packet summarizing your project state
2. Save it locally or in your own database
3. At the start of a new session (with any model), paste the packet
4. The model reconstructs context instantly — no re-explaining

### Automated (roadmap)
- CLI tool: converts chat export → ACTP packet automatically
- Compressor Agent: aggregates multiple packets into a single snapshot
- Relay Node: auto-syncs between AI tools via MCP

---

## Roadmap

| Status | Item |
|---|---|
| ✅ | Core concept validated |
| ✅ | v0.1 schema draft |
| ✅ | Symbolic encoding layer |
| ✅ | Node architecture spec (ACTP-N) |
| 🔄 | CLI: chat export → ACTP packet |
| ✅ | BENCH-001: Format vs constraint-following (3 models × 3 formats) |
| ✅ | BENCH-002: Anti-pattern lists fix model violations (3 models × 4 formats) |
| ⬜ | Compressor Agent (SaaS) |
| ⬜ | Maestro — multi-model orchestrator |
| ⬜ | actp.dev spec site |

## Benchmarks

ACTP constraint-following has been tested across Claude, ChatGPT, and Gemini.

### BENCH-001 — Format vs Constraint Following
**Constraint:** Model-agnostic, no provider SDK  
**Result:** Claude ✅ ChatGPT ✅ Gemini ❌ (all 3 formats)  
**Finding:** Gemini hardcoded OpenAI response shape regardless of format. Format alone cannot guarantee constraint following.

### BENCH-002 — Explicit Anti-Pattern Lists
**Constraint:** Same + explicit forbidden patterns with provider attribution  
**Result:** Claude ✅ ChatGPT ✅ Gemini ✅ (all 4 formats)  
**Finding:** Explicit anti-patterns fixed Gemini: 0/4 → 4/4. Constraint quality determines compliance, not format. Gemini internalized ACTP as native protocol — generating `actp_request`, `actp_payload`, `X-ACTP-Version` headers spontaneously.

> Full benchmark data: [`benchmarks/BENCH-002.md`](benchmarks/BENCH-002.md)
---

## Business Model

ACTP follows the **Git + GitHub model**:

| Layer | Price | Audience |
|---|---|---|
| Schema + CLI | Free / Open source | Developers |
| Compressor SaaS | ~$10–20/mo | AI power users |
| Enterprise | ~$100–500/mo | Companies with multi-model workflows |

The protocol is open. The tooling is where value is captured.

---

## Status

🚧 Early draft — open for discussion and contribution.

This spec was developed collaboratively across Claude, ChatGPT, and Gemini sessions — itself a live proof of concept for ACTP.

## Ideas / Roadmap

- **Session Tracking**: Add a `sessions` array to the spec that automatically logs each AI work session — start/end timestamps, summary of changes, decisions made, files modified. This enables full project history across AI sessions.

- **AI-to-AI Handoff**: Use session data to seamlessly transfer context between different AI models. Start a project with Claude, continue with ChatGPT, review with Gemini — without losing any context.

- **"Session End" Button**: Frontend implementations (like Maestro) can add a "Session Bitti" button that auto-generates an `.actp` JSON export of the current session, ready to import into any AI.

- **Multi-Model Synthesis Logging**: When multiple models answer the same question (orchestration tools), log each model's response and the synthesis result as part of the session record.

- **Import/Resume**: Load a previous `.actp` file to resume exactly where you left off — the AI reads the file and has full context of all past decisions, code state, and open questions.

## Contributing

Open an issue or PR. This is meant to become a community standard.

---

## About

**ACTP** is designed to make AI model switching as seamless as switching between apps. Your context belongs to you — not to any single model or platform.
