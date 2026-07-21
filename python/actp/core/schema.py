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
        }                "properties": {
                    "path": {
                        "type": "string",
                        "pattern": r"^(?!.*\.\.)[^/\\][^\x00]*$",
                        "description": "Relative path, no .. segments, no absolute paths"
                    },
                    "content": {"type": "string"},
                    "size": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "type": {"type": "string"},
                    "sha256": {
                        "type": "string",
                        "pattern": r"^[a-f0-9]{64}$"
                    }
                }
            }
        },
        "metadata": {
            "type": "object",
            "required": ["total_files", "total_tokens_estimate"],
            "properties": {
                "total_files": {
                    "type": "integer",
                    "minimum": 0
                },
                "total_tokens_estimate": {
                    "type": "integer",
                    "minimum": 0
                },
                "excluded_dirs": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "warnings": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "generator": {"type": "string"}
            }
        }
    }
}


class ACTPValidator:
    """ACTP paketlerini schema ve checksum'e karsi dogrular."""

    def __init__(self):
        self.schema = ACTP_SCHEMA

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Schema dogrulama. (is_valid, errors) doner."""
        if not HAS_JSONSCHEMA:
            return False, ["jsonschema kutuphanesi kurulu degil"]

        try:
            jsonschema.validate(
                instance=data,
                schema=self.schema,
                format_checker=FormatChecker()
            )
            return True, []
        except jsonschema.ValidationError as e:
            return False, [f"Schema hatasi: {e.message} (konum: {list(e.path)})"]
        except Exception as e:
            return False, [f"Dogrulama basarisiz: {str(e)}"]

    def validate_checksums(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """SHA-256 checksum'lari content ile karsilastir."""
        errors = []

        for file_entry in data.get("files", []):
            if "sha256" not in file_entry:
                continue  # sha256 opsiyonel

            expected = file_entry["sha256"]
            actual = hashlib.sha256(
                file_entry["content"].encode("utf-8")
            ).hexdigest()

            if expected != actual:
                errors.append(
                    f"Checksum uyusmazligi ({file_entry['path']}): "
                    f"beklenen={expected}, gercek={actual}"
                )

        return len(errors) == 0, errors

    @staticmethod
    def is_safe_path(base_dir: Path, target_path: Path) -> bool:
        """
        Path traversal kontrolu: target_path, base_dir disina cikiyor mu?
        resolve() symlink'leri de takip eder, normalize eder.
        """
        try:
            base_resolved = base_dir.resolve()
            target_resolved = target_path.resolve()
            return str(target_resolved).startswith(str(base_resolved))
        except (OSError, RuntimeError):
            return False
