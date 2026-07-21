import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from .schema import (
    ACTPPackage, ACTPFile, ACTPMetadata, 
    Decision, SymbolLegend, VocabularyEntry, OpenQuestion, Blocker
)

class ACTPPackager:
    IGNORE_PATTERNS = [
        '.git', '__pycache__', '.venv', 'node_modules',
        '.env', '.DS_Store', '*.pyc', '.pytest_cache',
        'dist', 'build', '*.egg-info'
    ]
    
    BINARY_EXTENSIONS = [
        '.bin', '.exe', '.dll', '.so', '.dylib',
        '.jpg', '.png', '.gif', '.zip', '.tar', '.gz'
    ]
    
    def __init__(self, project_name: str, version: str = "1.0.0"):
        self.project_name = project_name
        self.version = version
        self.files: List[ACTPFile] = []
        self.decisions: List[Decision] = []
        self.symbol_legend: List[SymbolLegend] = []
        self.vocabulary: List[VocabularyEntry] = []
        self.open_questions: List[OpenQuestion] = []
        self.blockers: List[Blocker] = []
        self.context: Dict[str, Any] = {}
    
    def _should_ignore(self, path: str) -> bool:
        for pattern in self.IGNORE_PATTERNS:
            if pattern in path:
                return True
        return False
    
    def _is_binary(self, file_path: Path) -> bool:
        ext = file_path.suffix.lower()
        if ext in self.BINARY_EXTENSIONS:
            return True
        
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(512)
                return b'\x00' in chunk
        except:
            return True
    
    def _calculate_checksum(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
    
    def add_file_from_path(self, file_path: Path) -> None:
        if self._should_ignore(str(file_path)):
            return
        
        if self._is_binary(file_path):
            file_type = 'binary'
            content = f"[Binary file - {file_path.name}]"
            file_bytes = b''
        else:
            file_type = 'code' if file_path.suffix in ['.py', '.js', '.ts', '.go', '.rs'] else 'text'
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            file_bytes = content.encode('utf-8')
        
        checksum = self._calculate_checksum(file_bytes)
        size = len(file_bytes)
        
        actp_file = ACTPFile(
            path=str(file_path),
            content=content,
            size=size,
            type=file_type,
            checksum=checksum
        )
        
        self.files.append(actp_file)
    
    def add_decision(self, id: str, title: str, description: str, context: str,
                    alternatives: List[str], rationale: str, date_made: Optional[str] = None,
                    impact: Optional[str] = None) -> None:
        decision = Decision(
            id=id,
            title=title,
            description=description,
            context=context,
            alternatives_considered=alternatives,
            rationale=rationale,
            date_made=date_made or datetime.now().isoformat(),
            impact=impact
        )
        self.decisions.append(decision)
    
    def add_symbol(self, symbol: str, meaning: str, usage_context: str,
                  related_symbols: Optional[List[str]] = None) -> None:
        legend = SymbolLegend(
            symbol=symbol,
            meaning=meaning,
            usage_context=usage_context,
            related_symbols=related_symbols or []
        )
        self.symbol_legend.append(legend)
    
    def add_vocabulary(self, term: str, definition: str, context: str,
                      aliases: Optional[List[str]] = None) -> None:
        vocab = VocabularyEntry(
            term=term,
            definition=definition,
            context=context,
            aliases=aliases or []
        )
        self.vocabulary.append(vocab)
    
    def add_open_question(self, id: str, question: str, context: str,
                         priority: str = "medium", related_decisions: Optional[List[str]] = None) -> None:
        q = OpenQuestion(
            id=id,
            question=question,
            context=context,
            priority=priority,
            related_decisions=related_decisions or []
        )
        self.open_questions.append(q)
    
    def add_blocker(self, id: str, title: str, description: str,
                   severity: str = "medium", related_decisions: Optional[List[str]] = None) -> None:
        blocker = Blocker(
            id=id,
            title=title,
            description=description,
            severity=severity,
            related_decisions=related_decisions or []
        )
        self.blockers.append(blocker)
    
    def set_context(self, context: Dict[str, Any]) -> None:
        self.context = context
    
    def calculate_vocabulary_hash(self) -> str:
        vocab_json = json.dumps(
            [v.__dict__ for v in self.vocabulary],
            sort_keys=True
        )
        return hashlib.sha256(vocab_json.encode()).hexdigest()
    
    def build(self) -> ACTPPackage:
        metadata = ACTPMetadata(
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=['actp', 'semantic', 'context']
        )
        
        vocab_hash = self.calculate_vocabulary_hash()
        
        package = ACTPPackage(
            version=self.version,
            project_name=self.project_name,
            files=self.files,
            metadata=metadata,
            decisions=self.decisions,
            symbol_legend=self.symbol_legend,
            vocabulary=self.vocabulary,
            open_questions=self.open_questions,
            blockers=self.blockers,
            context=self.context,
            vocabulary_hash=vocab_hash
        )
        
        return package
    
    def save_to_file(self, output_path: Path) -> None:
        package = self.build()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(package.to_dict(), f, indent=2, ensure_ascii=False)
