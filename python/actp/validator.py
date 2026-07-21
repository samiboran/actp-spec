import json
import hashlib
from pathlib import Path
from typing import Tuple, List

class ACTPValidator:
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
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
        
        self._validate_required_fields(data)
        self._validate_decisions(data.get('decisions', []))
        self._validate_symbol_legend(data.get('symbol_legend', []))
        self._validate_vocabulary(data.get('vocabulary', []))
        self._validate_open_questions(data.get('open_questions', []))
        self._validate_blockers(data.get('blockers', []))
        self._validate_checksums(data.get('files', []))
        self._validate_vocabulary_hash(data)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_required_fields(self, data: dict) -> None:
        required = ['version', 'project_name', 'files', 'metadata']
        for field in required:
            if field not in data:
                self.errors.append(f"Zorunlu alan eksik: {field}")
        
        if 'metadata' in data:
            meta = data['metadata']
            if 'created_at' not in meta:
                self.errors.append("metadata.created_at eksik")
            if 'updated_at' not in meta:
                self.errors.append("metadata.updated_at eksik")
    
    def _validate_decisions(self, decisions: list) -> None:
        if not isinstance(decisions, list):
            self.errors.append("decisions bir liste olmalı")
            return
        
        for i, decision in enumerate(decisions):
            required = ['id', 'title', 'description', 'context', 'alternatives_considered', 'rationale']
            for field in required:
                if field not in decision:
                    self.errors.append(f"Decision #{i} - {field} eksik")
            
            if not isinstance(decision.get('alternatives_considered', []), list):
                self.errors.append(f"Decision #{i} - alternatives_considered bir liste olmalı")
    
    def _validate_symbol_legend(self, symbols: list) -> None:
        if not isinstance(symbols, list):
            self.errors.append("symbol_legend bir liste olmalı")
            return
        
        for i, symbol in enumerate(symbols):
            required = ['symbol', 'meaning', 'usage_context']
            for field in required:
                if field not in symbol:
                    self.errors.append(f"Symbol #{i} - {field} eksik")
    
    def _validate_vocabulary(self, vocab: list) -> None:
        if not isinstance(vocab, list):
            self.errors.append("vocabulary bir liste olmalı")
            return
        
        for i, entry in enumerate(vocab):
            required = ['term', 'definition', 'context']
            for field in required:
                if field not in entry:
                    self.errors.append(f"Vocabulary #{i} - {field} eksik")
    
    def _validate_open_questions(self, questions: list) -> None:
        if not isinstance(questions, list):
            self.errors.append("open_questions bir liste olmalı")
            return
        
        for i, question in enumerate(questions):
            required = ['id', 'question', 'context', 'priority']
            for field in required:
                if field not in question:
                    self.errors.append(f"OpenQuestion #{i} - {field} eksik")
            
            if question.get('priority') not in ['high', 'medium', 'low']:
                self.warnings.append(f"OpenQuestion #{i} - priority bilinmiyor: {question.get('priority')}")
    
    def _validate_blockers(self, blockers: list) -> None:
        if not isinstance(blockers, list):
            self.errors.append("blockers bir liste olmalı")
            return
        
        for i, blocker in enumerate(blockers):
            required = ['id', 'title', 'description', 'severity']
            for field in required:
                if field not in blocker:
                    self.errors.append(f"Blocker #{i} - {field} eksik")
            
            if blocker.get('severity') not in ['critical', 'high', 'medium', 'low']:
                self.warnings.append(f"Blocker #{i} - severity bilinmiyor: {blocker.get('severity')}")
    
    def _validate_checksums(self, files: list) -> None:
        for i, file_obj in enumerate(files):
            if 'checksum' not in file_obj:
                self.warnings.append(f"File #{i} ({file_obj.get('path', '?')}) - checksum eksik")
                continue
            
            if file_obj.get('type') == 'binary':
                continue
            
            checksum = file_obj['checksum']
            if len(checksum) != 64 or not all(c in '0123456789abcdef' for c in checksum.lower()):
                self.errors.append(f"File #{i} - geçersiz checksum format: {checksum[:16]}...")
    
    def _validate_vocabulary_hash(self, data: dict) -> None:
        vocab_hash = data.get('vocabulary_hash', '')
        vocabulary = data.get('vocabulary', [])
        
        if not vocab_hash and vocabulary:
            self.warnings.append("vocabulary_hash boş ama vocabulary dolu")
            return
        
        if vocab_hash:
            vocab_json = json.dumps(vocabulary, sort_keys=True)
            calculated_hash = hashlib.sha256(vocab_json.encode()).hexdigest()
            
            if calculated_hash != vocab_hash:
                self.errors.append(
                    f"vocabulary_hash uyuşmuyor: {vocab_hash[:16]}... vs {calculated_hash[:16]}..."
                )
    
    def print_report(self) -> None:
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
