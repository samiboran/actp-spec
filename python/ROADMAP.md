ACTP Roadmap
Principle: Core protocol stays lean. Ecosystem features are built on top, not inside.
v0.2 — Schema Hardening (Next)
[ ] Extended secret scanner (GitLeaks patterns, 700+ rules)
[ ] actp diff — Compare two ACTP packages
[ ] actp merge — Merge multiple packages
[ ] Streaming read for large files (avoid RAM exhaustion)
[ ] Gzip/zstd optional compression plugin
v0.3 — Performance & Scale
[ ] Incremental update (only changed files)
[ ] Parallel processing for large repositories
[ ] Memory-mapped file I/O
[ ] Benchmark suite
v0.4 — Ecosystem Integration
[ ] MCP (Model Context Protocol) adapter
[ ] A2A (Agent-to-Agent) payload format
[ ] Agent Manifest parent_manifest reference
[ ] Microsoft APM apm_config reference
v0.5 — Artifact Registry
[ ] TONL/TOON format plugin (token-optimized notation)
[ ] Artifact marketplace / registry concept
[ ] Creative agent provenance extensions
[ ] Sigstore signing integration
v1.0 — Collective Intelligence (Future Vision)
[ ] Shared memory / Matrix layer
[ ] Stigmergic collaboration (ant pheromone model)
[ ] Reputation graph for agents
[ ] Decentralized P2P sync (IPFS, Hypercore)
Philosophy
Each version solves one class of problems well:
Table
Version	Focus	Question Answered
v0.1.x	Security & Validation	"Is this package safe and valid?"
v0.2.x	Tooling	"How do I compare, merge, optimize?"
v0.3.x	Performance	"Does it scale to 10k files?"
v0.4.x	Integration	"Does it work with MCP/A2A?"
v0.5.x	Extensions	"Can I use it for creative artifacts?"
v1.0.x	Collective	"Can agents learn from each other?"
We will not add v0.4+ features to v0.1.x. The core protocol stays stable.