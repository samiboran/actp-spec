"""
ACTP Packager - Projeleri JSON-LD uyumlu ACTP paketlerine dönüştür
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .schema import (
    ACTPPacket, ACTPFile, ACTPMetadata, ProjectDescriptor,
    Decision, SymbolLegend, Task, Artifacts, CodeSnippet,
    PriorityMatrixItem, DeadLetterItem
)


class ACTPPackager:
    """
    ACTP Packager - Projeyi pakete dönüştür
    - Dosyaları filtrele (binary, .git, node_modules, vb)
    - Kararları ve semantic katmanı yakala
    - JSON-LD uyumlu paket oluştur
    """
    
    IGNORE_PATTERNS = [
        '.git', '__pycache__', '.venv', 'node_modules',
        '.env', '.DS_Store', '*.pyc', '.pytest_cache',
        'dist', 'build', '*.egg-info', '.next', '.nuxt'
    ]
    
    BINARY_EXTENSIONS = [
        '.bin', '.exe', '.dll', '.so', '.dylib',
        '.jpg', '.png', '.gif', '.zip', '.tar', '.gz',
        '.wasm', '.pyc', '.o', '.a', '.lib'
    ]
    
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.md': 'markdown',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sh': 'shell',
    }
    
    def __init__(self, project_name: str = "", project_goal: str = ""):
        self.project_name = project_name
        self.project_goal = project_goal
        self.files: List[ACTPFile] = []
        self.decisions: List[Decision] = []
        self.symbol_legend: Dict[str, str] = {}
        self.tasks: List[Task] = []
        self.open_questions: List[str] = []
        self.next_steps: List[str] = []
        self.entity_map: Dict[str, str] = {}
        self.priority_matrix: List[PriorityMatrixItem] = []
    
    def _should_ignore(self, path: str) -> bool:
        """Dosya/dizin görmezden gelinmeli mi?"""
        for pattern in self.IGNORE_PATTERNS:
            if pattern.replace('*', '') in path:
                return True
        return False
    
    def _is_binary(self, file_path: Path) -> bool:
        """Dosya binary mi?"""
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
        """SHA-256 hash hesapla"""
        return hashlib.sha256(content).hexdigest()
    
    def _infer_language(self, path: str) -> str:
        """Dosya uzantısından dil türünü çıkar"""
        suffix = Path(path).suffix.lower()
        return self.LANGUAGE_MAP.get(suffix, suffix.lstrip('.') or 'text')
    
    def add_file(self, file_path: Path) -> Optional[ACTPFile]:
        """Dosyayı pakete ekle"""
        if self._should_ignore(str(file_path)):
            return None
        
        if self._is_binary(file_path):
            # Binary dosya - placeholder
            file_type = 'binary'
            content = f"[Binary file: {file_path.name}]"
            file_bytes = b''
        else:
            # Text/code dosya
            file_type = 'code' if file_path.suffix in ['.py', '.js', '.ts', '.go', '.rs', '.java'] else 'text'
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                file_bytes = content.encode('utf-8')
            except Exception as e:
                content = f"[Error reading file: {e}]"
                file_bytes = b''
        
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
        return actp_file
    
    def add_decision(
        self,
        id: str,
        priority: str,  # P0, P1, P2
        certainty: str,  # HIGH, MEDIUM, LOW
        mutability: str,  # LOCKED, FLEXIBLE
        content: str,
        symbol: Optional[str] = None,
        rationale: Optional[str] = None,
        source_model: Optional[str] = None,
        hallucination_risk: bool = False,
        external_dependency: bool = False
    ) -> Decision:
        """Karar ekle"""
        decision = Decision(
            id=id,
            priority=priority,
            certainty=certainty,
            mutability=mutability,
            content=content,
            symbol=symbol,
            rationale=rationale,
            source_model=source_model,
            hallucination_risk=hallucination_risk,
            external_dependency=external_dependency
        )
        self.decisions.append(decision)
        return decision
    
    def add_symbol(self, symbol: str, meaning: str, priority: Optional[str] = None,
                   mutability: Optional[str] = None, certainty: Optional[str] = None) -> None:
        """Sembol ekle"""
        # Format: "priority=P0, mutability=LOCKED, certainty=HIGH"
        parts = []
        if priority:
            parts.append(f"priority={priority}")
        if mutability:
            parts.append(f"mutability={mutability}")
        if certainty:
            parts.append(f"certainty={certainty}")
        
        symbol_value = ", ".join(parts) if parts else meaning
        self.symbol_legend[symbol] = symbol_value
    
    def add_task(self, id: str, status: str, description: str, symbol: Optional[str] = None) -> Task:
        """Görev ekle"""
        task = Task(id=id, status=status, description=description, symbol=symbol)
        self.tasks.append(task)
        return task
    
    def add_open_question(self, question: str) -> None:
        """Açık soru ekle"""
        self.open_questions.append(question)
    
    def add_next_step(self, step: str) -> None:
        """Sonraki adım ekle"""
        self.next_steps.append(step)
    
    def set_entity_map(self, entity_map: Dict[str, str]) -> None:
        """Kanonik ad haritası belirle"""
        self.entity_map = entity_map
    
    def add_priority_matrix_item(self, segment: str, weight: float) -> None:
        """Öncelik matrisi elemanı ekle"""
        if 0.0 <= weight <= 1.0:
            self.priority_matrix.append(PriorityMatrixItem(segment=segment, weight=weight))
    
    def calculate_vocabulary_hash(self) -> str:
        """
        Sözlük hash'i hesapla (symbol_legend'ten)
        """
        vocab_json = json.dumps(self.symbol_legend, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(vocab_json.encode('utf-8')).hexdigest()
    
    def build(self, created_by: Optional[str] = None, source_model: Optional[str] = None) -> ACTPPacket:
        """Paketi oluştur"""
        now = datetime.now().isoformat()
        
        # Proje tanımlayıcısı
        project = ProjectDescriptor(
            name=self.project_name,
            goal=self.project_goal,
            constraints=[],
            soft_preferences=[]
        )
        
        # Vocabulary hash hesapla
        vocab_hash = self.calculate_vocabulary_hash()
        
        # Metadata
        metadata = ACTPMetadata(
            created_at=now,
            created_by=created_by,
            model_context=source_model,
            tags=['actp', 'semantic', 'context']
        )
        
        code_snippets = [
            CodeSnippet(
                id=f"file-{index}",
                lang=self._infer_language(file.path),
                content=file.content,
                summary=file.path
            )
            for index, file in enumerate(self.files, start=1)
            if file.type == 'code'
        ]
        
        artifacts = Artifacts(code_snippets=code_snippets)
        
        # Paket oluştur
        packet = ACTPPacket(
            context="https://actp.dev/schema/v0.1",
            type="ACTPPacket",
            actp_version="0.1",
            created_at=now,
            project=project,
            decisions=self.decisions,
            vocabulary_hash=vocab_hash,
            symbol_legend=self.symbol_legend,
            source_model=source_model,
            tasks=self.tasks,
            files=self.files,
            artifacts=artifacts,
            open_questions=self.open_questions,
            next_steps=self.next_steps,
            entity_map=self.entity_map,
            priority_matrix=self.priority_matrix
        )
        
        return packet
    
    def save_to_file(self, output_path: Path, created_by: Optional[str] = None,
                     source_model: Optional[str] = None) -> None:
        """Paketi JSON dosyasına kaydet"""
        packet = self.build(created_by=created_by, source_model=source_model)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(packet.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """JSON dosyasından paket yükle"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


class ACTPPackagerFactory:
    """
    Fabrika - Dizinden paketi otomatik oluştur
    """
    
    @staticmethod
    def pack_directory(
        directory: Path,
        project_name: str,
        project_goal: str,
        created_by: Optional[str] = None,
        source_model: Optional[str] = None,
        max_depth: int = 10
    ) -> ACTPPacket:
        """
        Dizini pakete dönüştür
        """
        packager = ACTPPackager(project_name=project_name, project_goal=project_goal)
        
        # Dosyaları gez
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                # Depth kontrolü
                relative_path = file_path.relative_to(directory)
                depth = len(relative_path.parts)
                
                if depth <= max_depth:
                    actp_file = packager.add_file(file_path)
                    if actp_file:
                        actp_file.path = str(relative_path)
        
        return packager.build(created_by=created_by, source_model=source_model)
    
    @staticmethod
    def pack_directory_to_file(
        directory: Path,
        output_file: Path,
        project_name: str,
        project_goal: str,
        created_by: Optional[str] = None,
        source_model: Optional[str] = None,
        max_depth: int = 10
    ) -> None:
        """
        Dizini dosyaya pakele
        """
        packager = ACTPPackager(project_name=project_name, project_goal=project_goal)
        
        # Dosyaları gez
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(directory)
                depth = len(relative_path.parts)
                
                if depth <= max_depth:
                    actp_file = packager.add_file(file_path)
                    if actp_file:
                        actp_file.path = str(relative_path)
        
        packager.save_to_file(output_file, created_by=created_by, source_model=source_model)
