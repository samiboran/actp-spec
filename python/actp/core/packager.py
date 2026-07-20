import os
import json
import re
import hashlib
from pathlib import Path, PurePosixPath
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

try:
    import pathspec
    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False

from actp.core.schema import ACTPValidator


class ACTPPackager:
    EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                    'dist', 'build', '.pytest_cache', '.mypy_cache', '.tox'}
    EXCLUDE_FILES = {'.env', '.env.local', '.env.production', '.env.development',
                     '.env.test', '.env.staging', '.env.example', '.DS_Store',
                     'Thumbs.db', '*.pem', '*.key', '*.p12', '*.pfx'}
    BINARY_EXTENSIONS = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
        '.exe', '.dll', '.so', '.dylib', '.bin',
        '.mp3', '.mp4', '.avi', '.mov', '.wav', '.ogg',
        '.woff', '.woff2', '.ttf', '.eot', '.otf',
        '.db', '.sqlite', '.sqlite3', '.mdb',
        '.jar', '.war', '.ear',
        '.pyc', '.pyo',
        '.class',
    }
    SECRET_PATTERNS = [
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key'),
        (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Token'),
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    ]
    MAX_FILE_SIZE = 10_000_000  # 10 MB

    def __init__(self):
        self.gitignore_spec: Optional[Any] = None
        self.warnings: List[str] = []

    def pack(self, project_path: Path, max_depth: int = 3,
             strict_secrets: bool = False) -> Dict[str, Any]:
        self._load_gitignore(project_path)
        self.warnings = []

        context = {
            "version": "0.1.3",
            "project_name": project_path.name,
            "generated_at": self._timestamp(),
            "files": [],
            "metadata": {
                "total_files": 0,
                "total_tokens_estimate": 0,
                "excluded_dirs": [],
                "warnings": [],
                "generator": "actp-cli/0.1.3"
            }
        }

        for root, dirs, files in os.walk(project_path):
            # Kritik fix: Dizinleri buda
            original_dirs = dirs.copy()
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            excluded = set(original_dirs) - set(dirs)
            if excluded:
                context["metadata"]["excluded_dirs"].extend(excluded)

            depth = root[len(str(project_path)):].count(os.sep)
            if depth > max_depth:
                del dirs[:]
                continue

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(project_path)

                # Gitignore kontrolu (Windows uyumlu)
                if self._is_ignored(rel_path):
                    continue

                # Dosya adi kontrolu
                if file in self.EXCLUDE_FILES:
                    continue
                if any(file.endswith(ext.lstrip('*')) for ext in self.EXCLUDE_FILES if ext.startswith('*')):
                    continue

                # Binary filtreleme
                if any(file.lower().endswith(ext) for ext in self.BINARY_EXTENSIONS):
                    continue

                # Dosya boyutu limiti
                file_size = file_path.stat().st_size
                if file_size > self.MAX_FILE_SIZE:
                    self.warnings.append(
                        f"Dosya atlandi (boyut limiti): {rel_path} "
                        f"({file_size} > {self.MAX_FILE_SIZE} bytes)"
                    )
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except (UnicodeDecodeError, IOError):
                    continue

                # Secret taramasi
                secrets = self._scan_for_secrets(content, str(rel_path))
                if secrets:
                    self.warnings.extend(secrets)
                    if strict_secrets:
                        raise ValueError(f"Secrets found in {rel_path}: {secrets}")

                # SHA-256 checksum
                file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

                context["files"].append({
                    "path": str(rel_path),
                    "content": content,
                    "size": len(content),
                    "type": self._detect_type(file),
                    "sha256": file_hash
                })

                context["metadata"]["total_files"] += 1
                context["metadata"]["total_tokens_estimate"] += len(content) // 4

        context["metadata"]["warnings"] = self.warnings
        return context

    def unpack(self, data: Dict[str, Any], output_dir: Path):
        """ACTP paketini dizine cikarir - path traversal korumali."""
        output_dir.mkdir(parents=True, exist_ok=True)

        for file_info in data.get("files", []):
            file_path = output_dir / file_info["path"]

            # KRITIK: Path traversal kontrolu
            if not ACTPValidator.is_safe_path(output_dir, file_path):
                raise ValueError(
                    f"Path traversal tespit edildi: {file_info['path']} "
                    f"cikis dizininin disina cikiyor"
                )

            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info["content"])

    def _load_gitignore(self, project_path: Path):
        if not HAS_PATHSPEC:
            return
        gitignore_path = project_path / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                patterns = f.read().splitlines()
            self.gitignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def _is_ignored(self, rel_path: Path) -> bool:
        if not self.gitignore_spec:
            return False
        posix_path = str(PurePosixPath(rel_path))
        return self.gitignore_spec.match_file(posix_path)

    def _scan_for_secrets(self, content: str, file_path: str) -> List[str]:
        findings = []
        for pattern, name in self.SECRET_PATTERNS:
            if re.search(pattern, content):
                findings.append(f"Potential {name} in {file_path}")
        return findings

    def _detect_type(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        type_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.md': 'markdown', '.json': 'json', '.yaml': 'yaml',
            '.yml': 'yaml', '.rs': 'rust', '.go': 'go', '.sh': 'shell',
            '.toml': 'toml', '.ini': 'ini', '.css': 'css', '.html': 'html'
        }
        return type_map.get(ext, 'text')

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()
