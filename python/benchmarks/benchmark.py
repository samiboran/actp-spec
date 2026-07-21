"""ACTP Benchmark - Realistic token/time/cache efficiency.

Usage:
    python benchmark.py --all
"""
import argparse
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from actp.core.packager import ACTPPackager


class ACTPBenchmark:
    """Benchmark ACTP vs raw project sharing with realistic repos."""

    def __init__(self):
        self.packager = ACTPPackager()

    def generate_realistic_repo(self, root: Path, num_source_files: int = 100):
        """Generate a realistic repo with source + binary + excluded files."""
        dirs = ["src", "src/components", "src/utils", "tests", "docs", "config", "scripts"]
        for d in dirs:
            (root / d).mkdir(parents=True, exist_ok=True)
        
        file_types = [
            (".py", "def {name}():\n    return {value}\n\n"),
            (".js", "function {name}() {{\n  return {value};\n}}\n\n"),
            (".ts", "export const {name} = (): number => {value};\n\n"),
            (".md", "# {name}\n\nDocumentation for {name}.\n\n## Usage\n\nExample code here.\n\n"),
            (".json", '{{"name": "{name}", "value": {value}}}\n'),
            (".yaml", "{name}:\n  value: {value}\n"),
            (".css", ".{name} {{\n  color: #{value:06x};\n}}\n\n"),
            (".html", "<div class=\"{name}\">\n  <p>Content {value}</p>\n</div>\n\n"),
        ]
        
        for i in range(num_source_files):
            ext, template = file_types[i % len(file_types)]
            dir_name = dirs[i % len(dirs)]
            file_name = f"{dir_name}/file_{i:03d}{ext}"
            
            size = 200 + (i * 17) % 1800
            doc = "A" * (size // 4)
            content = template.format(name=f"func_{i}", value=i)
            while len(content) < size:
                content += f"// padding line {len(content)}\n"
            content = content[:size]
            
            file_path = root / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        
        # Binary files (EXCLUDED by ACTP)
        binary_dirs = ["assets", "dist", "build", "images"]
        for d in binary_dirs:
            (root / d).mkdir(exist_ok=True)
        
        binary_files = [
            ("assets/logo.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50000),
            ("assets/banner.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 80000),
            ("assets/icon.ico", b"\x00\x00\x01\x00" + b"\x00" * 20000),
            ("dist/bundle.js.map", b"{\"version\": 3}" + b"\x00" * 100000),
            ("dist/app.wasm", b"\x00asm\x01\x00\x00\x00" + b"\x00" * 50000),
            ("images/screenshot.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100000),
            ("build/output.zip", b"PK\x03\x04" + b"\x00" * 30000),
        ]
        
        for name, data in binary_files:
            (root / name).write_bytes(data)
        
        # Excluded directories
        (root / "node_modules" / "lodash").mkdir(parents=True, exist_ok=True)
        (root / "node_modules" / "lodash" / "index.js").write_text(
            "module.exports = require('./lodash');\n" * 1000, encoding="utf-8"
        )
        (root / "node_modules" / "react").mkdir(parents=True, exist_ok=True)
        (root / "node_modules" / "react" / "index.js").write_text(
            "module.exports = require('./react');\n" * 1000, encoding="utf-8"
        )
        
        (root / "__pycache__").mkdir(exist_ok=True)
        (root / "__pycache__" / "module.cpython-311.pyc").write_bytes(b"\x00" * 50000)
        
        (root / ".git" / "objects" / "ab").mkdir(parents=True, exist_ok=True)
        (root / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        
        (root / ".gitignore").write_text(
            "*.log\nnode_modules/\n__pycache__/\ndist/\n.env\n", 
            encoding="utf-8"
        )
        
        (root / ".env").write_text(
            "API_KEY=sk-test1234567890abcdef\nDB_PASSWORD=secret123\n",
            encoding="utf-8"
        )
        
        (root / "debug.log").write_text("ERROR: something\n" * 10000, encoding="utf-8")
        (root / "access.log").write_text("GET /api\n" * 20000, encoding="utf-8")
        
        return root

    def benchmark_without_actp(self, repo_path: Path, num_queries: int = 5) -> Dict:
        """Simulate: Every query reads ALL files."""
        print(f"\n[Without ACTP] {num_queries} queries")
        
        total_tokens = 0
        total_time = 0
        
        for q in range(num_queries):
            start = time.perf_counter()
            
            all_content = []
            for file_path in repo_path.rglob("*"):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        all_content.append(f"=== {file_path.relative_to(repo_path)} ===\n{content}")
                    except (UnicodeDecodeError, IOError):
                        pass
            
            raw_context = "\n\n".join(all_content)
            tokens = len(raw_context) // 4
            
            elapsed = time.perf_counter() - start
            total_tokens += tokens
            total_time += elapsed
            
            print(f"  Q{q+1}: {tokens:,} tokens, {elapsed:.3f}s")
        
        return {
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens // num_queries,
            "total_time": total_time,
            "avg_time": total_time / num_queries,
        }

    def benchmark_with_actp(self, repo_path: Path, num_queries: int = 5) -> Dict:
        """Simulate: Pack once, cache, reuse."""
        print(f"\n[With ACTP] {num_queries} queries")
        
        pack_start = time.perf_counter()
        packed = self.packager.pack(repo_path, max_depth=5)
        pack_time = time.perf_counter() - pack_start
        
        actp_file = repo_path.parent / "context.actp"
        with open(actp_file, "w") as f:
            json.dump(packed, f)
        
        total_tokens = 0
        total_time = 0
        
        for q in range(num_queries):
            start = time.perf_counter()
            
            with open(actp_file) as f:
                cached = json.load(f)
            
            context_parts = []
            for f in cached["files"]:
                context_parts.append(f"=== {f['path']} ===\n{f['content']}")
            
            actp_context = "\n\n".join(context_parts)
            tokens = len(actp_context) // 4
            
            elapsed = time.perf_counter() - start
            total_tokens += tokens
            total_time += elapsed
            
            print(f"  Q{q+1}: {tokens:,} tokens, {elapsed:.3f}s")
        
        actp_file.unlink(missing_ok=True)
        
        return {
            "pack_time": pack_time,
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens // num_queries,
            "total_time": total_time,
            "avg_time": total_time / num_queries,
            "warnings": len(packed.get("metadata", {}).get("warnings", [])),
        }

    def run(self, sizes: List[int] = None) -> Dict:
        """Run benchmark across repo sizes."""
        if sizes is None:
            sizes = [50, 100, 200]
        
        results = []
        
        for size in sizes:
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp) / f"repo_{size}"
                self.generate_realistic_repo(repo, num_source_files=size)
                
                print(f"\n{'='*70}")
                print(f"REPO: {size} source files + binaries + excluded dirs")
                print(f"{'='*70}")
                
                wo = self.benchmark_without_actp(repo, num_queries=5)
                wa = self.benchmark_with_actp(repo, num_queries=5)
                
                results.append({
                    "repo_size": size,
                    "without_actp": wo,
                    "with_actp": wa,
                    "token_savings": wo["total_tokens"] - wa["total_tokens"],
                    "token_savings_pct": round(
                        (wo["total_tokens"] - wa["total_tokens"]) / max(wo["total_tokens"], 1) * 100, 1
                    ),
                    "time_savings": wo["total_time"] - wa["total_time"],
                    "time_savings_pct": round(
                        (wo["total_time"] - wa["total_time"]) / max(wo["total_time"], 0.001) * 100, 1
                    ),
                })
        
        return {"benchmarks": results}

    def print_report(self, data: Dict):
        """Print formatted report."""
        print("\n" + "="*70)
        print("ACTP BENCHMARK REPORT")
        print("="*70)
        
        for r in