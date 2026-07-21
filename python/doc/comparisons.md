Ecosystem Comparisons
ACTP does not replace existing agent infrastructure. It complements it.
Positioning
plain
┌─────────────────────────────────────────┐
│         DECLARATION LAYER               │
│  Agent Manifest — "Who is this agent?"  │
│  Microsoft APM — "How is it configured?" │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         COMMUNICATION LAYER             │
│  MCP — "What tools can it use?"        │
│  A2A — "Who can it talk to?"           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         TRANSPORT LAYER                 │
│  ACTP — "What did it produce?"         │
│         "How do we move artifacts?"      │
└─────────────────────────────────────────┘
Detailed Comparison
vs Agent Manifest
Table
Agent Manifest	ACTP
Scope	Agent identity, boundaries, risk	Artifact content, integrity, transport
Format	manifest.json	*.actp
When	Pre-execution	Post-execution
Question	"Who is this agent?"	"What did this agent produce?"
Integration	metadata.parent_manifest	Reference in ACTP package
vs Microsoft APM
Table
Microsoft APM	ACTP
Scope	Agent setup, dependencies, policies	Artifact packaging, validation
Format	apm.yml, apm.lock.yaml	*.actp (JSON)
Command	apm install	actp pack/unpack/validate
Question	"How do I install this agent?"	"How do I move what it produced?"
Integration	metadata.apm_config	Reference in ACTP package
vs MCP (Model Context Protocol)
Table
MCP	ACTP
Scope	Tool access, capability discovery	Artifact transport
Layer	Tool/Resource layer	Payload layer
Example	"Call GitHub API"	"Package API response as artifact"
Integration	MCP outputs → ACTP packages	ACTP as MCP resource format
vs A2A (Agent-to-Agent)
Table
A2A	ACTP
Scope	Agent communication protocol	Message payload format
Layer	Transport/Protocol layer	Content/Payload layer
Example	"Send review request to agent B"	"The review report itself"
Integration	A2A message body = ACTP package	ACTP as A2A artifact attachment
Integration Examples
MCP + ACTP
Python
# MCP tool produces output
github_data = mcp_client.call("github.get_pr", {"repo": "my-app", "pr": 42})

# Package as ACTP artifact
actp.pack({"files": [{"path": "pr_42.json", "content": json.dumps(github_data)}]})
A2A + ACTP
JSON
{
  "message_type": "task_result",
  "from": "code-reviewer",
  "to": "dev-agent",
  "payload": {
    "format": "actp",
    "artifact_url": "https://registry.actp/review-42.actp",
    "checksum": "sha256:abc123..."
  }
}
Agent Manifest + ACTP
JSON
// ACTP package metadata
{
  "metadata": {
    "generator": "code-reviewer.v2",
    "parent_manifest": "https://agent-manifest.org/registry/code-reviewer.v2",
    "manifest_verified": true
  }
}
Key Insight
ACTP is the "envelope" that carries artifacts between agents. Other protocols define "who" and "how" — ACTP defines "what" is being carried and ensures it arrives intact.