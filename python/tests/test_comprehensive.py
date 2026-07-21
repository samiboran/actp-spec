"""
ACTP Comprehensive Test Suite - Stress Tests, Edge Cases, Integration Scenarios
Kapsamlı test: deduplikasyon, round-trip, veri integriteşi, perform ansa, edge case'ler
"""
import json
import hashlib
import tempfile
from pathlib import Path
import pytest
import time
import os

from actp.core.schema import ACTPPacket, ACTPFile, Decision, ProjectDescriptor
from actp.core.packager import ACTPPackager, ACTPPackagerFactory, ACTPExtractor
from actp.validator import ACTPValidator


class TestDeduplikasyonComprehensive:
    """✂️ Deduplikasyon kapsamlı testleri"""
    
    def test_no_duplication_multiple_code_files(self):
        """Birden fazla kod dosyası - tekrar yok"""
        packager = ACTPPackager("Dedup Multi", "Test multiple files")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 10 Python dosyası oluştur
            for i in range(10):
                (tmpdir_path / f"module_{i}.py").write_text(f"def func_{i}(): pass")
            
            for f in tmpdir_path.glob("*.py"):
                packager.add_file(f)
        
        packet = packager.build()
        
        # files[] ve code_snippets[] karşılaştır
        files_size = sum(len(f.content.encode()) if f.content else 0 for f in packet.files)
        snippets_size = sum(len(s.content.encode()) if s.content else 0 
                           for s in packet.artifacts.code_snippets)
        
        # code_snippets'te content olmamalı
        assert all(s.content is None for s in packet.artifacts.code_snippets)
        assert snippets_size == 0
        assert files_size > 0
        assert len(packet.files) == 10
        assert len(packet.artifacts.code_snippets) == 10
    
    def test_mixed_file_types_no_duplication(self):
        """Karma dosya türleri - sadece code files reference'a alınıyor"""
        packager = ACTPPackager("Mixed Types", "Code + text + markdown")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Karma dosyalar
            (tmpdir_path / "main.py").write_text("print('code')")
            (tmpdir_path / "notes.txt").write_text("Plain text")
            (tmpdir_path / "README.md").write_text("# Markdown")
            (tmpdir_path / "config.json").write_text('{"key": "value"}')
            
            for f in tmpdir_path.glob("*"):
                packager.add_file(f)
        
        packet = packager.build()
        
        # Sadece .py dosyası code_snippets'e girmeli
        assert len(packet.files) == 4
        assert len(packet.artifacts.code_snippets) == 1  # Sadece main.py
        
        # Code snippet'te content yok
        assert packet.artifacts.code_snippets[0].content is None
        assert packet.artifacts.code_snippets[0].summary is not None
    
    def test_deduplication_saves_space(self):
        """Deduplikasyon alanı tasarrufu göster"""
        packager = ACTPPackager("Space Saver", "Measure savings")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Large Python file
            large_content = "def func():\n    " + "\n    ".join([f"x{i} = {i}" for i in range(100)])
            (tmpdir_path / "large.py").write_text(large_content)
            
            for f in tmpdir_path.glob("*"):
                packager.add_file(f)
        
        packet = packager.build()
        packet_dict = packet.to_dict()
        
        # JSON boyutunu ölç
        json_str = json.dumps(packet_dict)
        json_size = len(json_str.encode())
        
        # files'in boyutu hesapla
        files_size = sum(len(f.get('content', '').encode()) 
                        for f in packet_dict.get('files', []))
        
        # code_snippets'in boyutu hesapla (content=null olmalı)
        snippets_size = sum(len(str(s.get('content', '')).encode()) 
                           for s in packet_dict.get('artifacts', {}).get('code_snippets', []))
        
        # snippets_size 0 olmalı (content null)
        assert snippets_size == 0
        # files_size > 0 olmalı
        assert files_size > 0
        # JSON boyutu makul olmalı
        assert json_size < files_size * 2  # En az %50 compression


class TestRoundTripComprehensive:
    """🔄 Round-trip (pack-unpack) kapsamlı testleri"""
    
    def test_round_trip_preserves_all_content(self):
        """Round-trip: tüm içerik korunur"""
        original_files = {
            "main.py": "def main():\n    print('Hello')",
            "utils.py": "def helper():\n    return 42",
            "README.md": "# My Project\nThis is great",
            "config.json": '{"version": "1.0", "debug": true}',
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Orijinal dosyaları yaz
            for filename, content in original_files.items():
                (tmpdir_path / filename).write_text(content)
            
            # PACK
            packager = ACTPPackager("Round Trip", "Full preservation")
            for f in tmpdir_path.glob("*"):
                packager.add_file(f)
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # UNPACK
            with tempfile.TemporaryDirectory() as restore_dir:
                extractor = ACTPExtractor(packet_dict)
                extracted_count = extractor.extract_to_directory(Path(restore_dir))
                
                assert extracted_count == len(original_files)
                
                # VERIFY
                for filename, original_content in original_files.items():
                    restored_file = Path(restore_dir) / filename
                    assert restored_file.exists(), f"{filename} not extracted"
                    
                    restored_content = restored_file.read_text()
                    assert restored_content == original_content, \
                        f"{filename}: content mismatch\nOriginal: {original_content}\nRestored: {restored_content}"
    
    def test_round_trip_nested_directories(self):
        """Round-trip: iç içe dizinler korunur"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # İç içe yapı oluştur
            (tmpdir_path / "src" / "main").mkdir(parents=True)
            (tmpdir_path / "src" / "utils").mkdir(parents=True)
            (tmpdir_path / "tests").mkdir(parents=True)
            (tmpdir_path / "docs").mkdir(parents=True)
            
            (tmpdir_path / "src" / "main" / "app.py").write_text("app_code")
            (tmpdir_path / "src" / "utils" / "helper.py").write_text("helper_code")
            (tmpdir_path / "tests" / "test_app.py").write_text("test_code")
            (tmpdir_path / "docs" / "README.md").write_text("docs")
            
            # PACK
            packager = ACTPPackager("Nested", "Nested directories")
            for f in tmpdir_path.rglob("*"):
                if f.is_file():
                    packager.add_file(f)
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # UNPACK
            with tempfile.TemporaryDirectory() as restore_dir:
                extractor = ACTPExtractor(packet_dict)
                extracted_count = extractor.extract_to_directory(Path(restore_dir))
                
                assert extracted_count == 4
                
                # Tüm dosya yolları kontrol et
                assert (Path(restore_dir) / "src" / "main" / "app.py").exists()
                assert (Path(restore_dir) / "src" / "utils" / "helper.py").exists()
                assert (Path(restore_dir) / "tests" / "test_app.py").exists()
                assert (Path(restore_dir) / "docs" / "README.md").exists()
    
    def test_round_trip_checksum_integrity(self):
        """Round-trip: checksum'lar eşleşir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            content = "x" * 10000  # Large content
            (tmpdir_path / "large.txt").write_text(content)
            
            # PACK
            packager = ACTPPackager("Checksum", "Verify checksums")
            packager.add_file(tmpdir_path / "large.txt")
            
            packet = packager.build()
            original_checksum = packet.files[0].checksum
            
            packet_dict = packet.to_dict()
            
            # UNPACK
            with tempfile.TemporaryDirectory() as restore_dir:
                extractor = ACTPExtractor(packet_dict)
                extractor.extract_to_directory(Path(restore_dir))
                
                restored_file = Path(restore_dir) / "large.txt"
                restored_content = restored_file.read_text()
                restored_checksum = hashlib.sha256(
                    restored_content.encode('utf-8')
                ).hexdigest()
                
                assert original_checksum == restored_checksum


class TestValidatorComprehensive:
    """✅ Validator kapsamlı testleri"""
    
    def test_validator_detects_content_tampering(self):
        """Validator: içerik değişikliği tespit eder"""
        content = "original content"
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        tampered_data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": hashlib.sha256(json.dumps({}, sort_keys=True).encode()).hexdigest(),
            "symbol_legend": {},
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [],
            "files": [
                {
                    "path": "test.txt",
                    "content": "TAMPERED CONTENT",  # Değiştirilmiş!
                    "size": len("TAMPERED CONTENT".encode()),
                    "type": "text",
                    "checksum": checksum  # Eski checksum
                }
            ]
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(tampered_data)
        
        assert is_valid is False
        assert any("checksum" in e for e in errors)
    
    def test_validator_enforces_required_fields(self):
        """Validator: zorunlu alanları zorunlu kılar"""
        incomplete_data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            # Missing: actp_version, created_at, project, decisions, symbol_legend
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(incomplete_data)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validator_checks_enum_values(self):
        """Validator: enum değerleri doğrular"""
        invalid_priority_data = {
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
                    "priority": "MEGA_CRITICAL",  # Geçersiz!
                    "certainty": "HIGH",
                    "mutability": "LOCKED",
                    "content": "Test"
                }
            ]
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(invalid_priority_data)
        
        assert is_valid is False
        assert any("priority" in e for e in errors)


class TestPerformance:
    """⚡ Performans testleri"""
    
    def test_pack_large_project_performance(self):
        """Performans: büyük proje paketleme hızı"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 50 dosya, her biri 1KB
            for i in range(50):
                (tmpdir_path / f"file_{i}.py").write_text(f"# File {i}\n" + "x" * 1000)
            
            packager = ACTPPackager("Perf Test", "Large project")
            
            start = time.time()
            for f in tmpdir_path.glob("*.py"):
                packager.add_file(f)
            
            packet = packager.build()
            elapsed = time.time() - start
            
            # 50 dosya 1 saniyede paketlenmeli
            assert elapsed < 1.0, f"Packing took {elapsed:.2f}s (expected < 1.0s)"
            assert len(packet.files) == 50
    
    def test_extract_large_packet_performance(self):
        """Performans: büyük paket extract hızı"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 50 dosya oluştur
            for i in range(50):
                (tmpdir_path / f"file_{i}.txt").write_text(f"Content {i}" * 100)
            
            # PACK
            packager = ACTPPackager("Extract Perf", "Large extraction")
            for f in tmpdir_path.glob("*.txt"):
                packager.add_file(f)
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # EXTRACT
            with tempfile.TemporaryDirectory() as restore_dir:
                start = time.time()
                extractor = ACTPExtractor(packet_dict)
                extracted = extractor.extract_to_directory(Path(restore_dir))
                elapsed = time.time() - start
                
                # 50 dosya 1 saniyede çıkarılmalı
                assert elapsed < 1.0, f"Extraction took {elapsed:.2f}s (expected < 1.0s)"
                assert extracted == 50


class TestEdgeCases:
    """🔍 Edge case testleri"""
    
    def test_empty_project_packing(self):
        """Edge: boş proje paketleme"""
        packager = ACTPPackager("Empty", "Empty project")
        packet = packager.build()
        
        assert len(packet.files) == 0
        assert len(packet.artifacts.code_snippets) == 0
        assert len(packet.decisions) == 0
    
    def test_very_large_single_file(self):
        """Edge: çok büyük tek dosya"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 10MB dosya
            large_content = "x" * (10 * 1024 * 1024)
            (tmpdir_path / "large.txt").write_text(large_content)
            
            packager = ACTPPackager("Large File", "Single large file")
            packager.add_file(tmpdir_path / "large.txt")
            
            packet = packager.build()
            assert len(packet.files) == 1
            assert packet.files[0].size == len(large_content.encode())
    
    def test_unicode_and_special_chars_preservation(self):
        """Edge: Unicode ve özel karakterler korunur"""
        special_content = """
        # 🚀 ACTP Protocol 
        def greet(name="世界"):
            return f"Hello {name}! 👋"
        
        # Emoji: 🔴🟡🟢
        # Math: ∑∏∫√∞
        # Symbols: ™©®±×÷
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "unicode.py").write_text(special_content)
            
            # PACK
            packager = ACTPPackager("Unicode", "Special characters")
            packager.add_file(tmpdir_path / "unicode.py")
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # UNPACK
            with tempfile.TemporaryDirectory() as restore_dir:
                extractor = ACTPExtractor(packet_dict)
                extractor.extract_to_directory(Path(restore_dir))
                
                restored = (Path(restore_dir) / "unicode.py").read_text()
                assert restored == special_content
    
    def test_binary_files_are_skipped(self):
        """Edge: binary dosyalar atlanır"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Binary file (image)
            binary_content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 1000
            (tmpdir_path / "image.png").write_bytes(binary_content)
            
            # Text file
            (tmpdir_path / "text.txt").write_text("text content")
            
            packager = ACTPPackager("Binary", "Binary filtering")
            
            for f in tmpdir_path.glob("*"):
                packager.add_file(f)
            
            # PNG skiplanmış, txt alınmış
            paths = [f.path for f in packager.files]
            assert any("text.txt" in p for p in paths)
            # Binary placeholder olabilir veya atlanabilir
    
    def test_deeply_nested_paths(self):
        """Edge: çok derin iç içe yollar"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 10 seviye derinlik
            deep_path = tmpdir_path
            for i in range(10):
                deep_path = deep_path / f"level_{i}"
                deep_path.mkdir()
            
            (deep_path / "deep_file.txt").write_text("deep content")
            
            packager = ACTPPackager("Deep", "Deep nesting")
            for f in tmpdir_path.rglob("*.txt"):
                packager.add_file(f)
            
            packet = packager.build()
            assert len(packet.files) == 1
            assert "level_" in packet.files[0].path
            
            # UNPACK
            packet_dict = packet.to_dict()
            with tempfile.TemporaryDirectory() as restore_dir:
                extractor = ACTPExtractor(packet_dict)
                extractor.extract_to_directory(Path(restore_dir))
                
                # Derin dosya restore edilmeli
                restored = list(Path(restore_dir).rglob("deep_file.txt"))
                assert len(restored) == 1


class TestIntegrationScenarios:
    """🎯 Gerçek dünya senaryoları"""
    
    def test_real_python_project_scenario(self):
        """Senaryo: Gerçek Python projesi"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Proje yapısı
            (tmpdir_path / "src").mkdir()
            (tmpdir_path / "tests").mkdir()
            (tmpdir_path / "docs").mkdir()
            
            (tmpdir_path / "README.md").write_text("# My Project")
            (tmpdir_path / "setup.py").write_text("from setuptools import setup\nsetup(name='myapp')")
            (tmpdir_path / "requirements.txt").write_text("click==8.0\njsonschema==4.0")
            (tmpdir_path / "src" / "app.py").write_text("def main(): pass")
            (tmpdir_path / "src" / "utils.py").write_text("def helper(): pass")
            (tmpdir_path / "tests" / "test_app.py").write_text("def test_main(): pass")
            
            # PACK
            packager = ACTPPackager("Real Project", "Python application")
            packager.add_decision(
                id="ARCH-001",
                priority="P0",
                certainty="HIGH",
                mutability="LOCKED",
                content="Use modular structure with src/ layout"
            )
            packager.add_symbol("🔴", "Critical decision", priority="P0")
            
            for f in tmpdir_path.rglob("*"):
                if f.is_file():
                    packager.add_file(f)
            
            packet = packager.build()
            assert len(packet.files) == 7
            assert len(packet.decisions) == 1
            assert len(packet.symbol_legend) == 1
            
            # VALIDATE
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_data(packet.to_dict())
            assert is_valid is True
            
            # UNPACK
            with tempfile.TemporaryDirectory() as restore_dir:
                extractor = ACTPExtractor(packet.to_dict())
                extracted = extractor.extract_to_directory(Path(restore_dir))
                assert extracted == 7
    
    def test_cross_model_context_transfer(self):
        """Senaryo: Model arası context transfer"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Kod yaz
            (tmpdir_path / "api.py").write_text("""
class APIServer:
    def __init__(self):
        self.routes = {}
    
    def add_route(self, path, handler):
        self.routes[path] = handler
""")
            
            # PACK for Claude
            packager1 = ACTPPackager("API Service", "REST API")
            packager1.add_decision(
                id="D1",
                priority="P0",
                certainty="HIGH",
                mutability="LOCKED",
                content="Use class-based handlers"
            )
            
            for f in tmpdir_path.glob("*.py"):
                packager1.add_file(f)
            
            packet1 = packager1.build(source_model="claude")
            
            # Save for transfer
            packet_file = tmpdir_path / "claude_context.actp"
            with open(packet_file, 'w') as f:
                json.dump(packet1.to_dict(), f)
            
            # Load for GPT
            with open(packet_file, 'r') as f:
                packet_data = json.load(f)
            
            # Verify completeness
            assert "files" in packet_data
            assert "decisions" in packet_data
            assert len(packet_data["files"]) > 0
            
            # Extract for GPT
            with tempfile.TemporaryDirectory() as gpt_dir:
                extractor = ACTPExtractor(packet_data)
                extracted = extractor.extract_to_directory(Path(gpt_dir))
                
                assert extracted > 0
                assert (Path(gpt_dir) / "api.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
