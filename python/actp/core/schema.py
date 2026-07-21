from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class ACTPFile:
    """ACTP paketi içindeki dosya"""
    path: str
    content: str
    size: int
    type: str  # 'text', 'binary', 'code'
    checksum: str  # SHA-256 hash

@dataclass
class Decision:
    """Proje kararları - semantik katman"""
    id: str
    title: str
    description: str
    context: str
    alternatives_considered: List[str]
    rationale: str
    date_made: Optional[str] = None
    impact: Optional[str] = None

@dataclass
class SymbolLegend:
    """Simgesel katman - önemli kavramlar/bileşenler"""
    symbol: str
    meaning: str
    usage_context: str
    related_symbols: List[str] = field(default_factory=list)

@dataclass
class VocabularyEntry:
    """Proje-spesifik kelime hazinesi"""
    term: str
    definition: str
    context: str
    aliases: List[str] = field(default_factory=list)

@dataclass
class OpenQuestion:
    """Açık sorular/belirsizlikler"""
    id: str
    question: str
    context: str
    priority: str  # 'high', 'medium', 'low'
    related_decisions: List[str] = field(default_factory=list)

@dataclass
class Blocker:
    """Engeller/sorunlar"""
    id: str
    title: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    related_decisions: List[str] = field(default_factory=list)

@dataclass
class ACTPMetadata:
    """Meta bilgiler"""
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    model_context: Optional[str] = None  # Hangi model için (Claude, GPT, etc)
    tags: List[str] = field(default_factory=list)

@dataclass
class ACTPPackage:
    """Ana ACTP paketi - JSON schema'ya uyumlu"""
    version: str  # "1.0.0"
    project_name: str
    
    # Temel içerik
    files: List[ACTPFile]
    metadata: ACTPMetadata
    
    # ⭐ SEMANTİK KATMAN
    decisions: List[Decision] = field(default_factory=list)
    symbol_legend: List[SymbolLegend] = field(default_factory=list)
    vocabulary: List[VocabularyEntry] = field(default_factory=list)
    open_questions: List[OpenQuestion] = field(default_factory=list)
    blockers: List[Blocker] = field(default_factory=list)
    
    # Context bilgisi
    context: Dict[str, Any] = field(default_factory=dict)  # Genel proje bağlamı
    vocabulary_hash: str = ""  # Sözlük tutarlılığı için
    
    def to_dict(self):
        """Paketi dictionary'ye çevir (JSON serialization için)"""
        return {
            'version': self.version,
            'project_name': self.project_name,
            'files': [
                {
                    'path': f.path,
                    'content': f.content,
                    'size': f.size,
                    'type': f.type,
                    'checksum': f.checksum,
                }
                for f in self.files
            ],
            'metadata': {
                'created_at': self.metadata.created_at,
                'updated_at': self.metadata.updated_at,
                'created_by': self.metadata.created_by,
                'model_context': self.metadata.model_context,
                'tags': self.metadata.tags,
            },
            'decisions': [
                {
                    'id': d.id,
                    'title': d.title,
                    'description': d.description,
                    'context': d.context,
                    'alternatives_considered': d.alternatives_considered,
                    'rationale': d.rationale,
                    'date_made': d.date_made,
                    'impact': d.impact,
                }
                for d in self.decisions
            ],
            'symbol_legend': [
                {
                    'symbol': s.symbol,
                    'meaning': s.meaning,
                    'usage_context': s.usage_context,
                    'related_symbols': s.related_symbols,
                }
                for s in self.symbol_legend
            ],
            'vocabulary': [
                {
                    'term': v.term,
                    'definition': v.definition,
                    'context': v.context,
                    'aliases': v.aliases,
                }
                for v in self.vocabulary
            ],
            'open_questions': [
                {
                    'id': q.id,
                    'question': q.question,
                    'context': q.context,
                    'priority': q.priority,
                    'related_decisions': q.related_decisions,
                }
                for q in self.open_questions
            ],
            'blockers': [
                {
                    'id': b.id,
                    'title': b.title,
                    'description': b.description,
                    'severity': b.severity,
                    'related_decisions': b.related_decisions,
                }
                for b in self.blockers
            ],
            'context': self.context,
            'vocabulary_hash': self.vocabulary_hash,
        }
