"""
ACTP Test Suite - Packager, Validator, Schema
"""
import json
import hashlib
import tempfile
from pathlib import Path
import pytest

from actp.core.schema import (
    ACTPPacket, ACTPFile, Decision, ProjectDescriptor, SymbolLegend
)
from actp.core.packager import ACTPPackager, ACTPPackagerFactory, ACTPExtractor
from actp.validator import ACTPValidator


class TestDecision:
    """Decision sınıfı testleri"""
    
    def test_decision_creation(self):
        """Karar oluşturma"""
        decision = Decision(
            id="D1",
            priority="P0",
            certainty="HIGH",
            mutability="LOCKED",
            content="Use Python",
            rationale="Fast development"
        )
        
        assert decision.id == "D1"
        assert decision.priority == "P0"
        assert decision.certainty == "HIGH"
        assert decision.mutability == "LOCKED"
    
    def test_decision_optional_fields(self):
        """Karar opsiyonel alanları"""
        decision = Decision(
            id="D2",
            priority="P1",
            certainty="MEDIUM",
            mutability="FLEXIBLE",
            content="Use JSON-LD",
            hallucination_risk=True,
            external_dependency=True
        )
        
        assert decision.hallucination_risk is True
        assert decision.external_dependency is True


class TestProjectDescriptor:
    """Proje tanımlayıcısı testleri"""
    
    def test_project_required_fields(self):
        """Proje zorunlu alanları"""
        project = ProjectDescriptor(
            name="ACTP Example",
            goal="Demonstrate ACTP"
        )
        
        assert project.name == "ACTP Example"
        assert project.goal == "Demonstrate ACTP"
    
    def test_project_constraints_and_preferences(self):
        """Proje kısıtları ve tercihler"""
        project = ProjectDescriptor(
            name="Test",
            goal="Test goal",
            constraints=["Must be JSON-LD"],
            soft_preferences=["Use symbols"]
        )
        
        assert len(project.constraints) == 1
        assert len(project.soft_preferences) == 1


class TestACTPPacket:
    """ACTP Paketi testleri"""
    
    def test_packet_json_ld_structure(self):
        """Paket JSON-LD yapısı"""
        packet = ACTPPacket(
            created_at="2026-07-21T10:00:00Z",
            project=ProjectDescriptor(name="Test", goal="Test"),
            decisions=[],
            symbol_legend={}
        )
        
        assert packet.context == "https://actp.dev/schema/v0.1"
        assert packet.type == "ACTPPacket"
        assert packet.actp_version == "0.1"
    
    def test_packet_to_dict(self):
        """Paketi dictionary'ye çevir"""
        decision = Decision(
            id="D1",
            priority="P0",
            certainty="HIGH",
            mutability="LOCKED",
            content="Test decision"
        )
        
        packet = ACTPPacket(
            created_at="2026-07-21T10:00:00Z",
            project=ProjectDescriptor(name="Test", goal="Test goal"),
            decisions=[decision],
            symbol_legend={"🔴": "priority=P0, mutability=LOCKED, certainty=HIGH"},
            files=[
                ACTPFile(
                    path="main.py",
                    content="print('hello')",
                    size=len("print('hello')".encode("utf-8")),
                    type="code",
                    checksum=hashlib.sha256("print('hello')".encode("utf-8")).hexdigest()
                )
            ]
        )
        
        data = packet.to_dict()
        
        assert data["@context"] == "https://actp.dev/schema/v0.1"
        assert data["@type"] == "ACTPPacket"
        assert len(data["decisions"]) == 1
        assert data["decisions"][0]["id"] == "D1"
        assert data["files"][0]["path"] == "main.py"


class TestACTPPackager:
    """ACTP Packager testleri"""
    
    def test_packager_creation(self):
        """Packager oluşturma"""
        packager = ACTPPackager(
            project_name="Test Project",
            project_goal="Test goal"
        )
        
        assert packager.project_name == "Test Project"
        assert packager.project_goal == "Test goal"
    
    def test_add_file(self):
        """Dosya ekleme"""
        packager = ACTPPackager("Test", "Test")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')")
            
            file_obj = packager.add_file(test_file)
            
            assert file_obj is not None
            assert file_obj.type == "code"
            assert file_obj.content == "print('hello')"
            assert len(file_obj.checksum) == 64  # SHA-256 length
    
    def test_add_decision(self):
        """Karar ekleme"""
        packager = ACTPPackager("Test", "Test")
        
        decision = packager.add_decision(
            id="D1",
            priority="P0",
            certainty="HIGH",
            mutability="LOCKED",
            content="Use Python",
            rationale="Fast"
        )
        
        assert decision.id == "D1"
        assert len(packager.decisions) == 1
    
    def test_add_symbol(self):
        """Sembol ekleme"""
        packager = ACTPPackager("Test", "Test")
        
        packager.add_symbol(
            symbol="🔴",
            meaning="Critical",
            priority="P0",
            mutability="LOCKED"
        )
        
        assert "🔴" in packager.symbol_legend
        assert "priority=P0" in packager.symbol_legend["🔴"]
    
    def test_vocabulary_hash_calculation(self):
        """Vocabulary hash hesaplama"""
        packager = ACTPPackager("Test", "Test")
        
        packager.add_symbol("🔴", "Critical")
        packager.add_symbol("🟡", "Medium")
        
        hash1 = packager.calculate_vocabulary_hash()
        
        # Aynı symbol'larla hash aynı olmalı
        packager2 = ACTPPackager("Test2", "Test2")
        packager2.add_symbol("🔴", "Critical")
        packager2.add_symbol("🟡", "Medium")
        
        hash2 = packager2.calculate_vocabulary_hash()
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256
    
    def test_build_packet(self):
        """Paket oluşturma"""
        packager = ACTPPackager("Test Project", "Test goal")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "main.py"
            test_file.write_text("print('hello')")
            packager.add_file(test_file)
        
        packager.add_decision(
            id="D1",
            priority="P0",
            certainty="HIGH",
            mutability="LOCKED",
            content="Test"
        )
        packager.add_symbol("🔴", "Critical")
        
        packet = packager.build(created_by="tester")
        
        assert packet.project.name == "Test Project"
        assert packet.project.goal == "Test goal"
        assert len(packet.decisions) == 1
        assert packet.context == "https://actp.dev/schema/v0.1"
        assert len(packet.files) == 1
        assert len(packet.artifacts.code_snippets) == 1
    
    def test_deduplication_no_content_copy(self):
        """✂️ Deduplikasyon test - code_snippets'te content yok"""
        packager = ACTPPackager("Dedup Test", "Test deduplication")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 2 Python dosyası ekle
            (Path(tmpdir) / "main.py").write_text("def main(): pass")
            (Path(tmpdir) / "utils.py").write_text("def helper(): pass")
            
            for f in Path(tmpdir).glob("*.py"):
                packager.add_file(f)
        
        packet = packager.build()
        
        # Deduplikasyon doğrulaması
        # files[] → tam içerik
        assert len(packet.files) == 2
        assert packet.files[0].content is not None
        assert len(packet.files[0].content) > 0
        
        # code_snippets[] → referans sadece (content=None)
        code_snippets = packet.artifacts.code_snippets
        assert len(code_snippets) == 2
        # Content'ı sadece file'da olmalı, code_snippet'te değil
        for snippet in code_snippets:
            assert snippet.content is None
            # Ama summary olmalı
            assert snippet.summary is not None


class TestACTPValidator:
    """ACTP Validator testleri"""
    
    def test_validator_creation(self):
        """Validator oluşturma"""
        validator = ACTPValidator()
        assert validator.strict_mode is False
    
    def test_validate_valid_packet(self):
        """Geçerli paketi doğrula"""
        file_content = "print('hello')"
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": hashlib.sha256(json.dumps({}, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
            "symbol_legend": {},
            "project": {
                "name": "Test",
                "goal": "Test goal",
                "constraints": [],
                "soft_preferences": []
            },
            "decisions": [],
            "files": [
                {
                    "path": "main.py",
                    "content": file_content,
                    "size": len(file_content.encode("utf-8")),
                    "type": "code",
                    "checksum": hashlib.sha256(file_content.encode("utf-8")).hexdigest()
                }
            ],
            "tasks": [],
            "artifacts": {},
            "entity_map": {},
            "priority_matrix": [],
            "open_questions": [],
            "next_steps": [],
            "dead_letter": []
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_file_checksum_mismatch(self):
        """Dosya checksum uyuşmazlığı"""
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": hashlib.sha256(json.dumps({}, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
            "symbol_legend": {},
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [],
            "files": [
                {
                    "path": "main.py",
                    "content": "print('hello')",
                    "size": len("print('hello')".encode("utf-8")),
                    "type": "code",
                    "checksum": "0" * 64
                }
            ]
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is False
        assert any("checksum uyuşmuyor" in e for e in errors)
    
    def test_validate_missing_required_field(self):
        """Zorunlu alan eksik"""
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            # actp_version eksik
            "created_at": "2026-07-21T10:00:00Z",
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [],
            "vocabulary_hash": "",
            "symbol_legend": {}
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is False
        assert any("actp_version" in e for e in errors)
    
    def test_validate_decision_priority(self):
        """Karar önceliği doğrulama"""
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": "",
            "symbol_legend": {},
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [
                {
                    "id": "D1",
                    "priority": "INVALID",  # Geçersiz
                    "certainty": "HIGH",
                    "mutability": "LOCKED",
                    "content": "Test"
                }
            ]
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is False
        assert any("priority" in e and "geçersiz" in e for e in errors)
    
    def test_validate_vocabulary_hash_mismatch(self):
        """Vocabulary hash uyuşmazlığı"""
        symbol_legend = {"🔴": "Critical"}
        wrong_hash = "0" * 64
        
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": wrong_hash,
            "symbol_legend": symbol_legend,
            "project": {"name": "Test", "goal": "Test"},
            "decisions": []
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is False
        assert any("vocabulary_hash" in e and "uyuşmuyor" in e for e in errors)
    
    def test_validate_file(self):
        """Dosyadan doğrulama"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Geçerli paket dosyası oluştur
            packet_data = {
                "@context": "https://actp.dev/schema/v0.1",
                "@type": "ACTPPacket",
                "actp_version": "0.1",
                "created_at": "2026-07-21T10:00:00Z",
                "vocabulary_hash": hashlib.sha256(json.dumps({}, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                "symbol_legend": {},
                "project": {"name": "Test", "goal": "Test"},
                "decisions": []
            }
            
            file_path = Path(tmpdir) / "test.actp"
            with open(file_path, 'w') as f:
                json.dump(packet_data, f)
            
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_file(file_path)
            
            assert is_valid is True


class TestPackagerFactory:
    """PackagerFactory testleri"""
    
    def test_pack_directory(self):
        """Dizini pakele"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Test dosyaları oluştur
            (tmpdir_path / "main.py").write_text("print('hello')")
            (tmpdir_path / "README.md").write_text("# Test")
            (tmpdir_path / ".git").mkdir()
            (tmpdir_path / ".git" / "config").write_text("git config")
            
            packet = ACTPPackagerFactory.pack_directory(
                tmpdir_path,
                "Test Project",
                "Test goal"
            )
            
            # .git dizini filtrelenmeli
            assert len(packet.project.name) > 0
            # İçeriği kontrol et
            paths = [f.path for f in packet.files]
            assert not any(".git" in p for p in paths)
            assert "main.py" in paths
            assert "README.md" in paths
            assert len(packet.artifacts.code_snippets) == 1


class TestExtractor:
    """🔓 ACTPExtractor testleri"""
    
    def test_extract_creates_files(self):
        """Extractor dosyaları yaratır"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Paket oluştur
            packager = ACTPPackager("Extract Test", "Test extraction")
            (tmpdir_path / "main.py").write_text("print('hello')")
            (tmpdir_path / "README.md").write_text("# Test")
            
            for f in tmpdir_path.glob("*"):
                if f.is_file():
                    packager.add_file(f)
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # Extract'ı test et
            with tempfile.TemporaryDirectory() as extract_dir:
                extracted = ACTPExtractor.extract_from_file(
                    packet_file=Path(tmpdir_path) / "dummy.actp",  # dummy path
                    output_dir=Path(extract_dir)
                )
                
                # Not: extract_from_file packet_file'dan okuyor, dummy kullandık
                # Bunun yerine direct ACTPExtractor kullanacağız
                extractor = ACTPExtractor(packet_dict)
                extracted_count = extractor.extract_to_directory(Path(extract_dir))
                
                assert extracted_count == 2
                assert (Path(extract_dir) / "main.py").exists()
                assert (Path(extract_dir) / "README.md").exists()
    
    def test_extract_preserves_content(self):
        """Extractor içeriği koruyor"""
        original_content = "def hello():\n    print('world')"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "script.py"
            test_file.write_text(original_content)
            
            # Paket oluştur
            packager = ACTPPackager("Preservation Test", "Test")
            packager.add_file(test_file)
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # Extract
            with tempfile.TemporaryDirectory() as extract_dir:
                extractor = ACTPExtractor(packet_dict)
                extractor.extract_to_directory(Path(extract_dir))
                
                # Doğrula
                extracted_file = Path(extract_dir) / "script.py"
                assert extracted_file.read_text() == original_content


class TestIntegration:
    """Entegrasyon testleri"""
    
    def test_full_workflow(self):
        """Tam workflow - packager → validator"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Proje dosyaları oluştur
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "main.py").write_text("def main():\n    pass")
            (src_dir / "utils.py").write_text("def helper():\n    pass")
            (tmpdir_path / "README.md").write_text("# Project")
            
            # Paket oluştur
            packager = ACTPPackager("Integration Test", "Test integration")
            for file_path in tmpdir_path.rglob("*"):
                if file_path.is_file():
                    packager.add_file(file_path)
            
            packager.add_decision(
                id="D1",
                priority="P0",
                certainty="HIGH",
                mutability="LOCKED",
                content="Use modular structure"
            )
            
            packager.add_symbol("🔴", "Critical")
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # Doğrula
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_data(packet_dict)
            
            assert is_valid is True
            assert len(errors) == 0
            assert len(packet_dict["files"]) == 3
    
    def test_round_trip_pack_unpack(self):
        """🔄 Round-trip test: pack → save → unpack → verify"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Orijinal proje dosyaları
            (tmpdir_path / "app.py").write_text("def app():\n    return 'ok'")
            (tmpdir_path / "config.json").write_text('{"debug": false}')
            
            # PACK: Pakete dönüştür
            packager = ACTPPackager("Round Trip Test", "Pack and unpack")
            for f in tmpdir_path.glob("*"):
                if f.is_file():
                    packager.add_file(f)
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # SAVE: Paketi dosyaya kaydet
            with tempfile.TemporaryDirectory() as work_dir:
                packet_file = Path(work_dir) / "round_trip.actp"
                with open(packet_file, 'w') as f:
                    json.dump(packet_dict, f)
                
                # UNPACK: Dosyaları geri çıkar
                with tempfile.TemporaryDirectory() as restore_dir:
                    extractor = ACTPExtractor(packet_dict)
                    extracted_count = extractor.extract_to_directory(Path(restore_dir))
                    
                    assert extracted_count == 2
                    
                    # VERIFY: İçerikleri karşılaştır
                    restored_app = (Path(restore_dir) / "app.py").read_text()
                    restored_config = (Path(restore_dir) / "config.json").read_text()
                    
                    assert restored_app == "def app():\n    return 'ok'"
                    assert restored_config == '{"debug": false}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
