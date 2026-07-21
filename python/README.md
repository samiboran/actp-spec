ACTP - Agent Context Transfer Protocol
v0.1.3 — Lightweight, model-agnostic artifact packaging for AI agents
https://github.com/samiboran/actp-spec/actions
https://www.python.org/
LICENSE
Quick Start
bash
pip install actp
actp pack . --output context.actp
actp validate context.actp --checksums
actp unpack context.actp --output-dir ./restored
What is ACTP?
ACTP is a standard format for packaging, validating, and transferring artifacts between AI agents.
✅ Secure: Path traversal protection, secret scanning, SHA-256 checksums
✅ Validated: JSON Schema enforcement, format checking
✅ Portable: Cross-platform, model-agnostic
✅ Lightweight: No cloud dependency, works offline
Architecture: MCP → A2A → ACTP
ACTP, Google'ın MCP (Model Context Protocol) ve A2A (Agent-to-Agent) protokollerinin tamamlayıcısıdır.
plain
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    MCP      │────→│    A2A      │────→│    ACTP     │
│  Tool Access│     │Agent Comm.  │     │Artifact Exch│
│  (Google)   │     │  (Google)   │     │   (ACTP)    │
└─────────────┘     └─────────────┘     └─────────────┘
Table
Katman	Protokol	Görev	Örnek
Tool Access	MCP	Ajanın araçları kullanması	"GitHub API'sini çağır"
Communication	A2A	Ajanlar arası mesajlaşma	"Kod review sonucunu gönder"
Artifact Exchange	ACTP	Ajan üretimlerinin taşınması	"Review raporunu paketle ve taşı"
Nasıl Çalışır?
MCP: Ajan, GitHub API'sini çağırarak PR bilgilerini alır
A2A: Ajan, başka bir ajana "bu PR'ı review et" mesajı gönderir
ACTP: Review sonucu (dosyalar, yorumlar, öneriler) .actp paketine konur ve hedef ajana iletilir
Fark Nedir?
Table
Soru	MCP	A2A	ACTP
"Ne yapabilirim?"	✅	❌	❌
"Kiminle konuşabilirim?"	❌	✅	❌
"Ne ürettim, nasıl taşırım?"	❌	❌	✅
ACTP, MCP ve A2A'nın payload katmanıdır — mesajın içeriğini standartlaştırır.
Features
Core (v0.1.3)
Table
Feature	Status	Description
actp pack	✅	Package project into .actp format
actp unpack	✅	Extract .actp with path traversal protection
actp inspect	✅	View package metadata
actp validate	✅	Schema + checksum verification
Secret Scanning	✅	OpenAI, AWS, GitHub key detection
.gitignore Respect	✅	Honors project exclusion rules
Binary Filtering	✅	Skips images, PDFs, compiled files
File Size Limit	✅	10MB default, configurable
Security
Python
# Path Traversal Protection
# Before: output_dir / "../../../.bashrc" → writes outside target!
# After:  raises ValueError("Path traversal detected")

# Secret Scanning
actp pack . --strict-secrets  # Fails if API keys found

# Checksum Verification
actp validate package.actp --checksums  # Verifies SHA-256 hashes
Installation
bash
git clone https://github.com/samiboran/actp-spec.git
cd actp-spec
pip install -e ".[dev]"
actp --version
Specification
JSON Schema v0.1.3 — Official format definition
Example Package — Sample .actp file
Ecosystem
ACTP works alongside existing agent infrastructure:
Table
Project	Role	Integration
MCP	Tool access	Package tool outputs as ACTP artifacts
A2A	Agent communication	ACTP as message payload format
Agent Manifest	Agent identity	metadata.parent_manifest reference
Microsoft APM	Agent configuration	metadata.apm_config reference
Roadmap
See ROADMAP.md for detailed version planning.
License
MIT