"""
ACTP Validator - JSON-LD uyumlu paketleri doğrula
"""
import json
import hashlib
from pathlib import Path
from typing import Tuple, List, Dict, Any


class ACTPValidator:
    """
    ACTP Paketi Validator
    - Zorunlu alanları kontrol et
    - Checksum'ları doğrula
    - Vocabulary hash'i doğrula
    - Karar alanlarını kontrol et
    """
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Dosyayı yükle ve doğrula"""
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON geçersiz: {e}")
            return False, self.errors, self.warnings
        except FileNotFoundError:
            self.errors.append(f"Dosya bulunamadı: {file_path}")
            return False, self.errors, self.warnings
        
        return self.validate_data(data)
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Veriyi doğrula"""
        self.errors = []
        self.warnings = []
        
        # JSON-LD zorunlu alanlar
        self._validate_json_ld_fields(data)
        
        # Proje tanımı
        self._validate_project(data.get('project', {}))
        
        # Kararlar
        self._validate_decisions(data.get('decisions', []))
        
        # Sembol sözlüğü ve hash
        self._validate_symbol_legend(data.get('symbol_legend', {}))
        self._validate_vocabulary_hash(data)
        
        # Tasks
        self._validate_tasks(data.get('tasks', []))
        
        # Files
        self._validate_files(data.get('files', []))
        
        # Artifacts
        self._validate_artifacts(data.get('artifacts', {}))
        
        # Diğer alanlar
        self._validate_optional_fields(data)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_json_ld_fields(self, data: dict) -> None:
        """JSON-LD zorunlu alanları kontrol et"""
        required = ['@context', '@type', 'actp_version', 'created_at', 'project', 'decisions', 'vocabulary_hash', 'symbol_legend']
        
        for field in required:
            if field not in data:
                self.errors.append(f"Zorunlu alan eksik: {field}")
        
        # Sabit değerleri kontrol et
        if data.get('@context') != 'https://actp.dev/schema/v0.1':
            self.errors.append(f"@context yanlış: {data.get('@context')}")
        
        if data.get('@type') != 'ACTPPacket':
            self.errors.append(f"@type yanlış: {data.get('@type')}")
        
        if data.get('actp_version') != '0.1':
            self.errors.append(f"actp_version yanlış: {data.get('actp_version')}")
    
    def _validate_project(self, project: dict) -> None:
        """Proje tanımını kontrol et"""
        if not isinstance(project, dict):
            self.errors.append("project bir dictionary olmalı")
            return
        
        required = ['name', 'goal']
        for field in required:
            if field not in project:
                self.errors.append(f"project.{field} eksik")
        
        # Optional alanlar
        if 'constraints' in project and not isinstance(project['constraints'], list):
            self.errors.append("project.constraints bir liste olmalı")
        
        if 'soft_preferences' in project and not isinstance(project['soft_preferences'], list):
            self.errors.append("project.soft_preferences bir liste olmalı")
    
    def _validate_decisions(self, decisions: list) -> None:
        """Kararları kontrol et"""
        if not isinstance(decisions, list):
            self.errors.append("decisions bir liste olmalı")
            return
        
        for i, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                self.errors.append(f"Decision #{i} bir dictionary olmalı")
                continue
            
            # Zorunlu alanlar
            required = ['id', 'priority', 'certainty', 'mutability', 'content']
            for field in required:
                if field not in decision:
                    self.errors.append(f"Decision #{i} - {field} eksik")
            
            # Enum kontrolü
            if 'priority' in decision and decision['priority'] not in ['P0', 'P1', 'P2']:
                self.errors.append(f"Decision #{i} - priority geçersiz: {decision['priority']}")
            
            if 'certainty' in decision and decision['certainty'] not in ['HIGH', 'MEDIUM', 'LOW']:
                self.errors.append(f"Decision #{i} - certainty geçersiz: {decision['certainty']}")
            
            if 'mutability' in decision and decision['mutability'] not in ['LOCKED', 'FLEXIBLE']:
                self.errors.append(f"Decision #{i} - mutability geçersiz: {decision['mutability']}")
    
    def _validate_symbol_legend(self, symbol_legend: dict) -> None:
        """Sembol sözlüğünü kontrol et"""
        if not isinstance(symbol_legend, dict):
            self.errors.append("symbol_legend bir dictionary olmalı")
            return
        
        # Her symbol değeri string olmalı
        for symbol, value in symbol_legend.items():
            if not isinstance(value, str):
                self.warnings.append(f"symbol_legend[{symbol}] string olmalı, {type(value).__name__} bulundu")
    
    def _validate_vocabulary_hash(self, data: dict) -> None:
        """Vocabulary hash'i doğrula"""
        vocab_hash = data.get('vocabulary_hash', '')
        symbol_legend = data.get('symbol_legend', {})
        
        if not vocab_hash and symbol_legend:
            self.warnings.append("vocabulary_hash boş ama symbol_legend dolu")
            return
        
        if vocab_hash:
            # Hash'i hesapla ve karşılaştır
            vocab_json = json.dumps(symbol_legend, sort_keys=True, ensure_ascii=False)
            calculated_hash = hashlib.sha256(vocab_json.encode('utf-8')).hexdigest()
            
            if calculated_hash != vocab_hash:
                self.errors.append(
                    f"vocabulary_hash uyuşmuyor: "
                    f"dosyadaki={vocab_hash[:16]}... "
                    f"hesaplanan={calculated_hash[:16]}..."
                )
    
    def _validate_tasks(self, tasks: list) -> None:
        """Görevleri kontrol et"""
        if not isinstance(tasks, list):
            self.errors.append("tasks bir liste olmalı")
            return
        
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                self.errors.append(f"Task #{i} bir dictionary olmalı")
                continue
            
            required = ['id', 'status', 'description']
            for field in required:
                if field not in task:
                    self.errors.append(f"Task #{i} - {field} eksik")
            
            if 'status' in task and task['status'] not in ['done', 'pending', 'blocked']:
                self.errors.append(f"Task #{i} - status geçersiz: {task['status']}")
    
    def _validate_files(self, files: list) -> None:
        """Dosyaları kontrol et"""
        if not isinstance(files, list):
            self.errors.append("files bir liste olmalı")
            return
        
        for i, file_data in enumerate(files):
            if not isinstance(file_data, dict):
                self.errors.append(f"File #{i} bir dictionary olmalı")
                continue
            
            required = ['path', 'content', 'size', 'type', 'checksum']
            for field in required:
                if field not in file_data:
                    self.errors.append(f"File #{i} - {field} eksik")
            
            if not isinstance(file_data.get('path'), str) or not file_data.get('path'):
                self.errors.append(f"File #{i} - path geçersiz")
            
            content = file_data.get('content')
            if not isinstance(content, str):
                self.errors.append(f"File #{i} - content string olmalı")
                continue
            
            size = file_data.get('size')
            if not isinstance(size, int) or size < 0:
                self.errors.append(f"File #{i} - size geçersiz")
            elif len(content.encode('utf-8')) != size:
                self.errors.append(f"File #{i} - size içeriğe uymuyor")
            
            checksum = file_data.get('checksum')
            if not isinstance(checksum, str) or len(checksum) != 64:
                self.errors.append(f"File #{i} - checksum geçersiz")
            else:
                calculated_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
                if calculated_checksum != checksum:
                    self.errors.append(f"File #{i} - checksum uyuşmuyor")
    
    def _validate_artifacts(self, artifacts: dict) -> None:
        """Artifacts'ı kontrol et"""
        if not isinstance(artifacts, dict):
            if artifacts:  # Boşsa warning yapma
                self.errors.append("artifacts bir dictionary olmalı")
            return
        
        # Code snippets
        code_snippets = artifacts.get('code_snippets', [])
        if not isinstance(code_snippets, list):
            self.errors.append("artifacts.code_snippets bir liste olmalı")
        else:
            for i, snippet in enumerate(code_snippets):
                if not isinstance(snippet, dict):
                    self.errors.append(f"CodeSnippet #{i} bir dictionary olmalı")
                    continue
                
                required = ['id', 'lang']
                for field in required:
                    if field not in snippet:
                        self.errors.append(f"CodeSnippet #{i} - {field} eksik")
                
                # content is optional (may be null when deduplicated into files[])
                if 'content' in snippet and snippet['content'] is not None:
                    if not isinstance(snippet['content'], str):
                        self.errors.append(f"CodeSnippet #{i} - content string veya null olmalı")
        
        # References
        references = artifacts.get('references', [])
        if not isinstance(references, list):
            self.errors.append("artifacts.references bir liste olmalı")
    
    def _validate_optional_fields(self, data: dict) -> None:
        """Opsiyonel alanları kontrol et"""
        # source_model
        if 'source_model' in data:
            valid_models = ['claude', 'chatgpt', 'gemini', 'other']
            if data['source_model'] not in valid_models:
                self.warnings.append(f"source_model bilinmiyor: {data['source_model']}")
        
        # open_questions
        open_questions = data.get('open_questions', [])
        if not isinstance(open_questions, list):
            self.errors.append("open_questions bir liste olmalı")
        
        # next_steps
        next_steps = data.get('next_steps', [])
        if not isinstance(next_steps, list):
            self.errors.append("next_steps bir liste olmalı")
        
        # entity_map
        entity_map = data.get('entity_map', {})
        if not isinstance(entity_map, dict):
            self.errors.append("entity_map bir dictionary olmalı")
        
        # priority_matrix
        priority_matrix = data.get('priority_matrix', [])
        if not isinstance(priority_matrix, list):
            self.errors.append("priority_matrix bir liste olmalı")
        else:
            for i, item in enumerate(priority_matrix):
                if not isinstance(item, dict):
                    self.errors.append(f"PriorityMatrixItem #{i} bir dictionary olmalı")
                    continue
                
                if 'segment' not in item or 'weight' not in item:
                    self.errors.append(f"PriorityMatrixItem #{i} - segment ve weight gerekli")
                
                if 'weight' in item:
                    weight = item['weight']
                    if not isinstance(weight, (int, float)) or not (0.0 <= weight <= 1.0):
                        self.errors.append(f"PriorityMatrixItem #{i} - weight 0.0-1.0 arasında olmalı")
    
    def print_report(self) -> None:
        """Doğrulama raporunu yazdır"""
        if self.errors:
            print("❌ HATALAR:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("⚠️  UYARILAR:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Tüm kontroller başarılı!")
