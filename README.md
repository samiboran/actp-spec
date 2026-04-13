# ACTP — AI Context Transfer Protocol

An open standard for exporting, importing, and transferring AI project context across different language models (Claude, ChatGPT, Gemini, etc.)

## The Problem

When switching between AI models or starting a new session, all project context is lost. Developers and AI power users waste significant time re-explaining their projects, decisions, and current state.

## The Solution

ACTP defines a portable `.actp` JSON format that captures the full semantic state of an AI-assisted project — decisions made, current code state, open questions — in a model-agnostic way.

## Format Spec (v0.1)

```json
{
  "actp_version": "0.1",
  "created_at": "ISO8601 timestamp",
  "project": {
    "name": "Project name",
    "description": "One paragraph summary"
  },
  "decisions": [
    { "topic": "...", "decision": "...", "rationale": "..." }
  ],
  "current_state": "Plain text summary of where the project is right now",
  "code_snapshot": {
    "files": [
      { "path": "src/index.js", "summary": "..." }
    ]
  },
  "open_questions": ["...", "..."],
  "next_steps": ["...", "..."]
}
\```

## Status

🚧 Early draft — open for discussion and contribution.

## Contributing

Open an issue or PR. This is meant to be a community standard.
