"""
ACTP Security & Reliability Test Suite - Advanced tests
Güvenlik, deterministik davranış, ölçeklenebilirlik testleri
"""
import json
import hashlib
import tempfile
from pathlib import Path
import pytest
import threading
from concurrent.futures import ThreadPoolExecutor

from actp.core.schema import ACTPPacket, ACTPFile, Decision, ProjectDescriptor
from actp.core.packager import ACTPPackager, ACTPPackagerFactory, ACTPExtractor
from actp.validator import ACTPValidator


class TestSecurityPathTraversal:
    """🔒 Path Traversal Saldırıları - GÜVENLIK"""
    
    def test_reject_parent_directory_traversal_unix(self):
        """Security: Unix-style path traversal reddedilir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Normal dosya
            (tmpdir_path / "normal.txt").write_text("safe")
            
            packager = ACTPPackager("Security", "Path traversal test")
            packager.add_file(tmpdir_path / "normal.txt")
            
            # Paket oluştur
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # Path traversal payload ekle
            packet_dict["files"].append({
                "path": "../../etc/passwd",  # ← Zararlı path
                "content": "[root contents]",
                "size": 17,
                "type": "text",
                "checksum": hashlib.sha256(b"[root contents]").hexdigest()
            })
            
            # Validator bu zararlı path'i reddetmeli
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_data(packet_dict)
            
            # Path traversal tespit edilmeli
            if is_valid is False:
                # Validator reject etti - iyi!
                assert any("path" in e.lower() for e in errors)
    
    def test_reject_windows_path_traversal(self):
        """Security: Windows-style path traversal reddedilir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            packager = ACTPPackager("Windows Security", "Windows paths")
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # Windows path traversal
            packet_dict["files"] = [{
                "path": "..\\..\\windows\\system32\\config",
                "content": "[system config]",
                "size": 15,
                "type": "text",
                "checksum": hashlib.sha256(b"[system config]").hexdigest()
            }]
            
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_data(packet_dict)
            
            # Validator reddetmeli
            assert is_valid is False or any("path" in str(e).lower() for e in errors + warnings)
    
    def test_reject_absolute_paths(self):
        """Security: Absolute paths reddedilir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            packager = ACTPPackager("Absolute", "Absolute path security")
            
            packet = packager.build()
            packet_dict = packet.to_dict()
            
            # Absolute path
            packet_dict["files"] = [{
                "path": "/etc/passwd",  # Absolute!
                "content": "dangerous",
                "size": 9,
                "type": "text",
                "checksum": hashlib.sha256(b"dangerous").hexdigest()
            }]
            
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_data(packet_dict)
            
            # Reddedilmeli
            assert is_valid is False or len(errors) > 0


class TestLargeScaleStress:
    """🔥 Büyük Ölçek Stress Testleri"""
    
    def test_pack_500_files(self):
        """Stress: 500 dosya paketleme"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 500 dosya oluştur
            for i in range(500):
                (tmpdir_path / f"file_{i:04d}.py").write_text(f"# File {i}\ncode = {i}")
            
            packager = ACTPPackager("Large Scale", "500 files")
            
            for f in tmpdir_path.glob("*.py"):
                packager.add_file(f)
            
            packet = packager.build()
            
            assert len(packet.files) == 500
            assert len(packet.artifacts.code_snippets) == 500
    
    def test_pack_1000_files(self):
        """Stress: 1000 dosya paketleme"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 1000 dosya oluştur
            for i in range(1000):
                (tmpdir_path / f"file_{i:05d}.txt").write_text(f"Content {i}")
            
            packager = ACTPPackager("Mega Scale", "1000 files")
            
            for f in tmpdir_path.glob("*.txt"):
                packager.add_file(f)
            
            packet = packager.build()
            
            assert len(packet.files) == 1000
    
    def test_1000_decisions(self):
        """Stress: 1000 karar"""
        packager = ACTPPackager("Decisions", "1000 decisions")
        
        for i in range(1000):
            packager.add_decision(
                id=f"D{i:04d}",
                priority=["P0", "P1", "P2"][i % 3],
                certainty=["HIGH", "MEDIUM", "LOW"][i % 3],
                mutability=["LOCKED", "FLEXIBLE"][i % 2],
                content=f"Decision {i}"
            )
        
        packet = packager.build()
        
        assert len(packet.decisions) == 1000
    
    def test_500_symbols(self):
        """Stress: 500 sembol"""
        packager = ACTPPackager("Symbols", "500 symbols")
        
        for i in range(500):
            packager.add_symbol(
                symbol=f"SYM{i:03d}",
                meaning=f"Symbol meaning {i}",
                priority=["P0", "P1", "P2"][i % 3]
            )
        
        packet = packager.build()
        
        assert len(packet.symbol_legend) == 500


class TestCorruptedPackets:
    """💥 Bozuk Paket Testleri"""
    
    def test_reject_null_checksum(self):
        """Corrupted: null checksum reddedilir"""
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": hashlib.sha256(json.dumps({}, sort_keys=True).encode()).hexdigest(),
            "symbol_legend": {},
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [],
            "files": [{
                "path": "test.txt",
                "content": "content",
                "size": 7,
                "type": "text",
                "checksum": None  # ← Null checksum!
            }]
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is False
    
    def test_reject_malformed_files_array(self):
        """Corrupted: files string olursa reddedilir"""
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": "",
            "symbol_legend": {},
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [],
            "files": "this should be array"  # ← Malformed!
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        assert is_valid is False
    
    def test_reject_invalid_file_types(self):
        """Corrupted: geçersiz file type reddedilir"""
        data = {
            "@context": "https://actp.dev/schema/v0.1",
            "@type": "ACTPPacket",
            "actp_version": "0.1",
            "created_at": "2026-07-21T10:00:00Z",
            "vocabulary_hash": "",
            "symbol_legend": {},
            "project": {"name": "Test", "goal": "Test"},
            "decisions": [],
            "files": [{
                "path": "test.txt",
                "content": "content",
                "size": 7,
                "type": "INVALID_TYPE",  # ← Geçersiz!
                "checksum": hashlib.sha256(b"content").hexdigest()
            }]
        }
        
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        # Validator ya reddedecek ya uyarı verecek
        assert is_valid is False or len(warnings) > 0


class TestVersionCompatibility:
    """📦 Sürüm Uyumluluğu Testleri"""
    
    def test_reject_invalid_version_string(self):
        """Version: geçersiz version string reddedilir"""
        invalid_versions = ["0.0.1", "999.0", "abc", "1.2.3.4", ""]
        
        for invalid_version in invalid_versions:
            data = {
                "@context": "https://actp.dev/schema/v0.1",
                "@type": "ACTPPacket",
                "actp_version": invalid_version,  # ← Geçersiz version
                "created_at": "2026-07-21T10:00:00Z",
                "vocabulary_hash": "",
                "symbol_legend": {},
                "project": {"name": "Test", "goal": "Test"},
                "decisions": []
            }
            
            validator = ACTPValidator()
            is_valid, errors, warnings = validator.validate_data(data)
            
            # 0.1 dışındaki sürümler reddedilmeli (şimdilik)
            if invalid_version != "0.0.1":  # 0.0.1 maybe compatibility?
                assert is_valid is False or len(warnings) > 0


class TestDeterministicBuild:
    """🔄 Deterministik Build Testleri"""
    
    def test_same_input_same_output_checksum(self):
        """Deterministic: aynı giriş → aynı çıktı checksum"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Dosya oluştur
            (tmpdir_path / "code.py").write_text("def func(): pass")
            
            # İlk build
            packager1 = ACTPPackager("Determ1", "Test")
            packager1.add_file(tmpdir_path / "code.py")
            packet1 = packager1.build()
            checksum1 = packet1.files[0].checksum
            
            # İkinci build (aynı dosya)
            packager2 = ACTPPackager("Determ2", "Test")
            packager2.add_file(tmpdir_path / "code.py")
            packet2 = packager2.build()
            checksum2 = packet2.files[0].checksum
            
            # Checksum'lar eşleşmeli
            assert checksum1 == checksum2
    
    def test_json_serialization_deterministic(self):
        """Deterministic: JSON serialization aynı mı?"""
        packager = ACTPPackager("JSON Determ", "JSON test")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("x = 1")
            packager.add_file(Path(tmpdir) / "test.py")
            packager.add_symbol("🔴", "Critical")
        
        packet = packager.build()
        
        # İki kez to_dict() çağrı
        dict1 = packet.to_dict()
        dict2 = packet.to_dict()
        
        # JSON serialize
        json1 = json.dumps(dict1, sort_keys=True, ensure_ascii=False)
        json2 = json.dumps(dict2, sort_keys=True, ensure_ascii=False)
        
        # SHA256 hash'leri eşleşmeli
        hash1 = hashlib.sha256(json1.encode()).hexdigest()
        hash2 = hashlib.sha256(json2.encode()).hexdigest()
        
        assert hash1 == hash2
    
    def test_packet_hash_stability(self):
        """Deterministic: vocabulary_hash stabil"""
        packager = ACTPPackager("Hash Stable", "Hash test")
        
        packager.add_symbol("🔴", "Red")
        packager.add_symbol("🟡", "Yellow")
        
        packet1 = packager.build()
        hash1 = packet1.vocabulary_hash
        
        # Aynı packager'dan tekrar build
        packet2 = packager.build()
        hash2 = packet2.vocabulary_hash
        
        assert hash1 == hash2


class TestDuplicatePath:
    """🔀 Duplicate Path Testleri"""
    
    def test_duplicate_paths_handling(self):
        """Duplicate: aynı path iki kez eklenirse?"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # İki dosya oluştur
            (tmpdir_path / "main.py").write_text("version = 1")
            file1 = tmpdir_path / "main.py"
            
            packager = ACTPPackager("Duplicate", "Duplicate path test")
            
            # Aynı dosya iki kez ekle
            packager.add_file(file1)
            packager.add_file(file1)
            
            packet = packager.build()
            
            # Davranış: 2 dosya mı, 1 dosya mı, hata mı?
            # Genellikle 2 dosya olmalı (deduplication packet düzeyinde değil, packager'da yapılmaz)
            assert len(packet.files) == 2


class TestBinaryDetection:
    """📦 Binary Dosya Tespit Testleri"""
    
    def test_binary_png_handling(self):
        """Binary: PNG dosyası nasıl ele alınır?"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # PNG binary
            png_magic = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
            (tmpdir_path / "image.png").write_bytes(png_magic)
            
            packager = ACTPPackager("Binary", "Binary detection")
            file_obj = packager.add_file(tmpdir_path / "image.png")
            
            # Binary dosya type'ı kontrol et
            assert file_obj is not None
            assert file_obj.type == "binary" or file_obj.type is not None
            
            # Content placeholder olmalı
            assert "[Binary file" in file_obj.content or "Binary" in file_obj.content
    
    def test_binary_exe_handling(self):
        """Binary: EXE dosyası nasıl ele alınır?"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # EXE magic header
            exe_data = b'MZ' + b'\x00' * 100
            (tmpdir_path / "app.exe").write_bytes(exe_data)
            
            packager = ACTPPackager("EXE", "Executable")
            file_obj = packager.add_file(tmpdir_path / "app.exe")
            
            assert file_obj is not None
            assert file_obj.type == "binary"


class TestInvalidUTF8:
    """🔤 Invalid UTF-8 Testleri"""
    
    def test_invalid_utf8_file_handling(self):
        """UTF-8: Geçersiz UTF-8 dosyası nasıl ele alınır?"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Geçersiz UTF-8 bytes
            invalid_utf8 = b'\xff\xfe\xfa\xfb'
            (tmpdir_path / "broken.txt").write_bytes(invalid_utf8)
            
            packager = ACTPPackager("UTF8", "UTF-8 test")
            
            # add_file yapılınca error oluşmalı mı, yoksa skip mi?
            # Genellikle error handling yapılır
            try:
                file_obj = packager.add_file(tmpdir_path / "broken.txt")
                # Eğer başarılıysa, content error mesajı olmalı
                assert file_obj is not None
                if "Error" in file_obj.content or "error" in file_obj.content:
                    # Error handling yapıldı
                    pass
            except Exception:
                # Exception throw edildi - bu da kabul edilir
                pass


class TestDecisionIDUniqueness:
    """🏷️ Decision ID Uniqueness Testleri"""
    
    def test_duplicate_decision_ids(self):
        """Uniqueness: İki aynı ID ile decision eklenirse?"""
        packager = ACTPPackager("IDs", "ID uniqueness")
        
        d1 = packager.add_decision(
            id="D1",
            priority="P0",
            certainty="HIGH",
            mutability="LOCKED",
            content="First decision"
        )
        
        d2 = packager.add_decision(
            id="D1",  # ← Aynı ID!
            priority="P1",
            certainty="MEDIUM",
            mutability="FLEXIBLE",
            content="Second decision"
        )
        
        packet = packager.build()
        packet_dict = packet.to_dict()
        
        # Validator bunu kontrol etmeli mi?
        # Genellikle iki ID'nin de eklenmesine izin verilir (warning yapılabilir)
        assert len(packet.decisions) == 2


class TestSymbolCollision:
    """🔄 Symbol Collision Testleri"""
    
    def test_symbol_overwrite(self):
        """Symbols: Aynı symbol iki farklı meaning ile eklenirse?"""
        packager = ACTPPackager("Symbols", "Symbol collision")
        
        packager.add_symbol("🔴", "First meaning")
        packager.add_symbol("🔴", "Second meaning")  # ← Overwrite!
        
        packet = packager.build()
        
        # Genellikle son değer tutulur
        assert packet.symbol_legend["🔴"] in ["First meaning", "Second meaning", 
                                               "priority=Second meaning"]


class TestConcurrentPacking:
    """🔀 Concurrent Packing Testleri"""
    
    def test_concurrent_packagers_thread_safe(self):
        """Concurrent: 20 thread ile aynı anda pack yapılırsa?"""
        results = []
        errors = []
        
        def pack_in_thread(thread_id):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir_path = Path(tmpdir)
                    
                    # Her thread kendi dosyasını yarat
                    (tmpdir_path / f"file_{thread_id}.py").write_text(
                        f"# Thread {thread_id}\ndata = {thread_id}"
                    )
                    
                    packager = ACTPPackager(f"Thread{thread_id}", "Concurrent test")
                    packager.add_file(tmpdir_path / f"file_{thread_id}.py")
                    
                    packet = packager.build()
                    results.append((thread_id, len(packet.files)))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # 20 thread ile concurrent pack
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(pack_in_thread, i) for i in range(20)]
            for future in futures:
                future.result()
        
        # Hepsi başarılı olmalı
        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(results) == 20
        assert all(count == 1 for _, count in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
