# CLI v0.2 Implementation Plan

## New Commands

### actp capture
actp capture "decision content" --symbol ??
Appends decision to packet. Symbol sets priority.

### actp rehydrate
actp rehydrate ./context.actp.json
Outputs formatted prompt header for cross-model transfer.

### actp save
actp save --message "commit message"
Saves versioned snapshot.

### actp diff
actp diff v1.actp.json v2.actp.json
Compares two packet versions.

### actp merge
actp merge a.actp.json b.actp.json
Merges packets using D9 conflict resolution.

### actp sync
actp sync --push / --pull
Syncs with cloud. Requires actp login.

## Implementation Order
1. capture (LOW complexity)
2. rehydrate (LOW complexity)
3. save (MEDIUM)
4. diff (MEDIUM)
5. sync (HIGH)
6. merge (HIGH)
