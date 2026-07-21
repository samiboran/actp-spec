"""
ACTP Core Schema - Python dataclasses aligned with root actp.schema.json
Implements JSON-LD structure, semantic decision fields, and project hierarchy.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============================================================================
# JSON-LD & Semantic Layer - Heart of ACTP
# ============================================================================

@dataclass
class Decision:
    """
    Karar - ACTP'nin kalbi.
    Root schema'daki zorunlu alanlar: id, priority, certainty, mutability, content
    """
    id: str
    priority: str  # "P0" (kritik), "P1" (yüksek), "P2" (düşük)
    certainty: str  # "HIGH", "MEDIUM", "LOW"
    mutability: str  # "LOCKED" (değişmemeli), "FLEXIBLE"
    content: str  # Kararın kendisi
    
    # Optional
    symbol: Optional[str] = None  # 🔴, 🟡, 🔵, vb.
    rationale: Optional[str] = None  # Neden bu karar?
    source_model: Optional[str] = None  # Hangi model yaptı? (claude, chatgpt, gemini)
    hallucination_risk: bool = False  # 🌫️ Düşük emin - yanılma riski
    external_dependency: bool = False  # 🔗 Dış kaynağa bağlı mı?


@dataclass
class SymbolLegend:
    """Sembol sözlüğü - emoji/simgeler → anlamlar"""
    symbol: str
    meaning: str
    priority: Optional[str] = None  # P0, P1, P2
    mutability: Optional[str] = None  # LOCKED, FLEXIBLE
    certainty: Optional[str] = None  # HIGH, MEDIUM, LOW


@dataclass
class ProjectDescriptor:
    """
    Proje tanımı - bağlamın zirvesi (apex).
    Root schema zorunlu: name, goal
    """
    name: str  # Proje adı
    goal: str  # Bir cümle: Bu proje ne yapmak istiyor?
    
    # Optional
    constraints: List[str] = field(default_factory=list)  # 🔴 Değişmez kurallar
    soft_preferences: List[str] = field(default_factory=list)  # 🟡 Esnek tercihler


@dataclass
class Task:
    """Görev/İş"""
    id: str
    status: str  # "done", "pending", "blocked"
    description: str
    symbol: Optional[str] = None


@dataclass
class CodeSnippet:
    """Kod parçacığı"""
    id: str
    lang: str  # python, typescript, etc
    content: Optional[str] = None  # None when deduplicated — full content lives in files[]
    summary: Optional[str] = None


@dataclass
class CodeGraphRef:
    """Yapısal kod grafiğine referans (opsiyonel)"""
    tool: str  # "graphify", vs
    graph_path: str  # Dosya yolu
    graph_hash: Optional[str] = None  # SHA-256
    generated_at: Optional[str] = None  # ISO8601
    node_count: Optional[int] = None


@dataclass
class Artifacts:
    """Kod ve referanslar"""
    code_snippets: List[CodeSnippet] = field(default_factory=list)
    references: List[str] = field(default_factory=list)  # URL'ler, dosyalar
    code_graph_ref: Optional[CodeGraphRef] = None


@dataclass
class PriorityMatrixItem:
    """Öncelik matrisi - hangi bölüme odaklanılmalı?"""
    segment: str
    weight: float  # 0.0 - 1.0


@dataclass
class DeadLetterItem:
    """Karantinaya alınan context (çözülememiş)"""
    id: str
    reason: str
    original: str


@dataclass
class ACTPFile:
    """Dosya - pakette taşınan içerik"""
    path: str
    content: str
    size: int
    type: str  # 'text', 'binary', 'code'
    checksum: str  # SHA-256


@dataclass
class ACTPMetadata:
    """Meta bilgiler"""
    created_at: str  # ISO8601
    created_by: Optional[str] = None
    model_context: Optional[str] = None  # claude, chatgpt, gemini
    tags: List[str] = field(default_factory=list)


# ============================================================================
# Main ACTP Packet - JSON-LD compatible
# ============================================================================

@dataclass
class ACTPPacket:
    """
    ACTP Paketi - ana konteyner.
    Root actp.schema.json'a tam uyumlu.
    """
    # JSON-LD & Core (sabit - root schema'da const)
    context: str = "https://actp.dev/schema/v0.1"  # @context
    type: str = "ACTPPacket"  # @type
    actp_version: str = "0.1"  # Protokol versiyonu
    
    # Zorunlu alanlar
    created_at: str = ""  # ISO8601
    project: ProjectDescriptor = field(default_factory=lambda: ProjectDescriptor(name="", goal=""))
    decisions: List[Decision] = field(default_factory=list)
    vocabulary_hash: str = ""  # SHA-256 hash
    symbol_legend: Dict[str, str] = field(default_factory=dict)  # emoji → açıklama
    
    # Optional
    source_model: Optional[str] = None  # claude, chatgpt, gemini, other
    tasks: List[Task] = field(default_factory=list)
    files: List[ACTPFile] = field(default_factory=list)
    artifacts: Artifacts = field(default_factory=Artifacts)
    entity_map: Dict[str, str] = field(default_factory=dict)  # Kanonik adlar
    priority_matrix: List[PriorityMatrixItem] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)  # Açık sorular
    next_steps: List[str] = field(default_factory=list)  # Sonraki adımlar
    dead_letter: List[DeadLetterItem] = field(default_factory=list)
    integrity_hash: Optional[str] = None  # SHA-256 tüm içeriğin

    def to_dict(self) -> Dict[str, Any]:
        """Paketi JSON-LD uyumlu dictionary'ye çevir"""
        return {
            "@context": self.context,
            "@type": self.type,
            "actp_version": self.actp_version,
            "created_at": self.created_at,
            "source_model": self.source_model,
            "vocabulary_hash": self.vocabulary_hash,
            "symbol_legend": self.symbol_legend,
            "project": {
                "name": self.project.name,
                "goal": self.project.goal,
                "constraints": self.project.constraints,
                "soft_preferences": self.project.soft_preferences,
            },
            "decisions": [
                {
                    "id": d.id,
                    "priority": d.priority,
                    "certainty": d.certainty,
                    "mutability": d.mutability,
                    "content": d.content,
                    "symbol": d.symbol,
                    "rationale": d.rationale,
                    "source_model": d.source_model,
                    "hallucination_risk": d.hallucination_risk,
                    "external_dependency": d.external_dependency,
                }
                for d in self.decisions
            ],
            "tasks": [
                {
                    "id": t.id,
                    "status": t.status,
                    "description": t.description,
                    "symbol": t.symbol,
                }
                for t in self.tasks
            ],
            "files": [
                {
                    "path": f.path,
                    "content": f.content,
                    "size": f.size,
                    "type": f.type,
                    "checksum": f.checksum,
                }
                for f in self.files
            ],
            "artifacts": {
                "code_snippets": [
                    {
                        "id": cs.id,
                        "lang": cs.lang,
                        "content": cs.content,
                        "summary": cs.summary,
                    }
                    for cs in self.artifacts.code_snippets
                ],
                "references": self.artifacts.references,
                "code_graph_ref": (
                    {
                        "tool": self.artifacts.code_graph_ref.tool,
                        "graph_path": self.artifacts.code_graph_ref.graph_path,
                        "graph_hash": self.artifacts.code_graph_ref.graph_hash,
                        "generated_at": self.artifacts.code_graph_ref.generated_at,
                        "node_count": self.artifacts.code_graph_ref.node_count,
                    }
                    if self.artifacts.code_graph_ref
                    else None
                ),
            },
            "entity_map": self.entity_map,
            "priority_matrix": [
                {"segment": pm.segment, "weight": pm.weight}
                for pm in self.priority_matrix
            ],
            "open_questions": self.open_questions,
            "next_steps": self.next_steps,
            "dead_letter": [
                {
                    "id": dl.id,
                    "reason": dl.reason,
                    "original": dl.original,
                }
                for dl in self.dead_letter
            ],
            "integrity_hash": self.integrity_hash,
        }
