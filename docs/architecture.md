# ACTP Application Architecture

**Decision source:** BENCH-002 consensus (Claude + ChatGPT + Gemini)

## Platform Roadmap
- Phase 1: CLI (v0.1 complete)
- Phase 2: VS Code Extension
- Phase 3: Web App (actp.dev)

## Data Architecture

### Local (offline-first)
~/.actp/
  config.json
  packets/
    <project-name>/
      current.actp.json
      versions/

### Cloud (optional sync)
- PostgreSQL: users, packets, versions
- Conflict resolution: D9 branch-both + vector clocks
- P0 tie: human-in-the-loop, no silent auto-merge

## New User Onboarding
npm install -g actp
actp init -n "my-project"
actp capture "first decision" --symbol ??
actp save --message "Initial setup"
actp login
actp sync --push
actp rehydrate context.actp.json

## UX Philosophy (ChatGPT)
- File-based workflow
- Transparent JSON
- No hidden state
- AI optional layer

ACTP is not an AI chat interface.
ACTP is an AI workflow state manager.
