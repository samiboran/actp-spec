# ACTP Ideas & Future Considerations

## Budget Constraint System
Add enforcement layer alongside priority:
```json
{
  "max_critical_items": 5,
  "max_total_tokens": 1500
}

Forces the system to choose — not just rank.
Context Ranking Engine
Priority (🔴🟠🟡) + Budget + Compression = real decision making:
What stays
What gets summarized
What gets dropped
Recency Weight
New information gets slight advantage:

score = importance * 0.7 + recency * 0.3
new context.
These are v1.0+ ideas. Current spec is v0.4 stable.
