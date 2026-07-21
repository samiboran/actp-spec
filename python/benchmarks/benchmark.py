"""
ACTP Benchmark - Realistic token/time efficiency comparison.

Compares:
1. Raw file reading (without ACTP)
2. ACTP-packaged context (with semantic decisions + caching)

Usage:
    python benchmark.py --all
    python benchmark.py --sizes 50 100 200 500
"""
import argparse
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from actp.core.packager import ACTPPackagerFactory
from actp.validator import ACTPValidator


class ACTPBenchmark:
    """Benchmark ACTP vs raw project sharing."""

    def __init__(self):
        self.validator = ACTPValidator()

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
            content = template.format(name=f"func_{i}", value=i)
            while len(content) < size:
                content += f"// comment line\n"
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
            ("dist/bundle.js.map", b"{\"version\": 3}" + b"\x00" * 100000),
            ("images/screenshot.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100000),
        ]
        
        for name, data in binary_files:
            (root / name).write_bytes(data)
        
        # Excluded directories
        (root / "node_modules" / "lodash").mkdir(parents=True, exist_ok=True)
        (root / "node_modules" / "lodash" / "index.js").write_text(
            "module.exports = require('./lodash');\n" * 1000, encoding="utf-8"
        )
        
        (root / "__pycache__").mkdir(exist_ok=True)
        (root / "__pycache__" / "module.cpython-311.pyc").write_bytes(b"\x00" * 50000)
        
        (root / ".git" / "objects" / "ab").mkdir(parents=True, exist_ok=True)
        (root / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        
        return root

    def benchmark_without_actp(self, repo_path: Path, num_queries: int = 5) -> Dict:
        """Baseline: Every query reads ALL files (simulating context window resets)."""
        print(f"\n📊 [Without ACTP] {num_queries} queries")
        
        total_tokens = 0
        total_time = 0
        total_size = 0
        file_count = 0
        
        for q in range(num_queries):
            start = time.perf_counter()
            
            all_content = []
            for file_path in sorted(repo_path.rglob("*")):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        all_content.append(f"=== {file_path.relative_to(repo_path)} ===\n{content}")
                        if q == 0:
                            file_count += 1
                            total_size += len(content)
                    except (UnicodeDecodeError, IOError):
                        pass
            
            raw_context = "\n\n".join(all_content)
            tokens = len(raw_context) // 4  # Rough approximation
            
            elapsed = time.perf_counter() - start
            total_tokens += tokens
            total_time += elapsed
            
            print(f"   Q{q+1}: {tokens:,} tokens | {elapsed:.3f}s")
        
        return {
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens // num_queries,
            "total_time": total_time,
            "avg_time": total_time / num_queries,
            "file_count": file_count,
            "total_size": total_size,
        }

    def benchmark_with_actp(self, repo_path: Path, num_queries: int = 5) -> Dict:
        """ACTP: Pack once, cache, reuse across queries."""
        print(f"\n📦 [With ACTP] {num_queries} queries")
        
        # PACK
        pack_start = time.perf_counter()
        packet = ACTPPackagerFactory.pack_directory(
            directory=repo_path,
            project_name="Benchmark Project",
            project_goal="Performance comparison",
            max_depth=5
        )
        pack_time = time.perf_counter() - pack_start
        
        # VALIDATE
        packet_dict = packet.to_dict()
        is_valid, errors, warnings = self.validator.validate_data(packet_dict)
        
        if not is_valid:
            print(f"   ⚠️  Validation errors: {len(errors)}")
            return {"error": errors}
        
        # SAVE
        actp_file = repo_path.parent / "context.actp"
        actp_size = 0
        with open(actp_file, 'w', encoding='utf-8') as f:
            json.dump(packet_dict, f, indent=2, ensure_ascii=False)
            actp_size = actp_file.stat().st_size
        
        print(f"   📝 Packed in {pack_time:.3f}s | File size: {actp_size:,} bytes")
        
        total_tokens = 0
        total_time = 0
        
        for q in range(num_queries):
            start = time.perf_counter()
            
            # LOAD & RECONSTRUCT
            with open(actp_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # Simulate context reconstruction
            context_parts = []
            
            # Project info
            project = cached.get('project', {})
            context_parts.append(f"Project: {project.get('name', 'Unknown')}\nGoal: {project.get('goal', 'Unknown')}")
            
            # Decisions
            for decision in cached.get('decisions', [])[:10]:  # Top 10
                context_parts.append(f"Decision {decision.get('id', '?')}: {decision.get('content', '')}")
            
            # Artifacts (code snippets)
            artifacts = cached.get('artifacts', {})
            for snippet in artifacts.get('code_snippets', [])[:5]:  # Top 5
                context_parts.append(f"Code [{snippet.get('id')}]:\n{snippet.get('content', '')}")
            
            actp_context = "\n\n".join(context_parts)
            tokens = len(actp_context) // 4
            
            elapsed = time.perf_counter() - start
            total_tokens += tokens
            total_time += elapsed
            
            print(f"   Q{q+1}: {tokens:,} tokens | {elapsed:.3f}s")
        
        actp_file.unlink(missing_ok=True)
        
        return {
            "pack_time": pack_time,
            "actp_size": actp_size,
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens // num_queries,
            "total_time": total_time,
            "avg_time": total_time / num_queries,
            "validation_warnings": len(warnings),
        }

    def run(self, sizes: List[int] = None, num_queries: int = 5) -> Dict:
        """Run benchmark across repo sizes."""
        if sizes is None:
            sizes = [50, 100, 200]
        
        results = []
        
        for size in sizes:
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp) / f"repo_{size}"
                self.generate_realistic_repo(repo, num_source_files=size)
                
                print(f"\n{'='*70}")
                print(f"📁 REPO: {size} source files + binaries + excluded")
                print(f"{'='*70}")
                
                wo = self.benchmark_without_actp(repo, num_queries=num_queries)
                wa = self.benchmark_with_actp(repo, num_queries=num_queries)
                
                if "error" not in wa:
                    token_savings = wo["total_tokens"] - wa["total_tokens"]
                    token_savings_pct = round(
                        token_savings / max(wo["total_tokens"], 1) * 100, 1
                    )
                    time_savings = wo["total_time"] - wa["total_time"]
                    time_savings_pct = round(
                        time_savings / max(wo["total_time"], 0.001) * 100, 1
                    )
                    
                    results.append({
                        "repo_size": size,
                        "without_actp": wo,
                        "with_actp": wa,
                        "token_savings": token_savings,
                        "token_savings_pct": token_savings_pct,
                        "time_savings": time_savings,
                        "time_savings_pct": time_savings_pct,
                    })
        
        return {"benchmarks": results}

    def print_report(self, data: Dict):
        """Print formatted report."""
        print("\n" + "="*70)
        print("✨ ACTP BENCHMARK REPORT")
        print("="*70)
        
        for r in data.get("benchmarks", []):
            size = r["repo_size"]
            wo = r["without_actp"]
            wa = r["with_actp"]
            
            print(f"\n📊 Repo Size: {size} files")
            print(f"   {'─' * 66}")
            
            print(f"\n   WITHOUT ACTP (baseline)")
            print(f"      Files indexed: {wo.get('file_count', 'N/A')}")
            print(f"      Total size: {wo.get('total_size', 0) / 1024 / 1024:.2f} MB")
            print(f"      Avg tokens/query: {wo.get('avg_tokens', 0):,}")
            print(f"      Avg time/query: {wo.get('avg_time', 0):.3f}s")
            
            print(f"\n   WITH ACTP (packed)")
            print(f"      ACTP file size: {wa.get('actp_size', 0) / 1024:.1f} KB")
            print(f"      Pack time: {wa.get('pack_time', 0):.3f}s")
            print(f"      Avg tokens/query: {wa.get('avg_tokens', 0):,}")
            print(f"      Avg time/query: {wa.get('avg_time', 0):.3f}s")
            
            print(f"\n   💾 SAVINGS")
            print(f"      Token reduction: {r['token_savings']:,} ({r['token_savings_pct']}%)")
            print(f"      Time reduction: {r['time_savings']:.3f}s ({r['time_savings_pct']}%)")
            
            print(f"\n   {'─' * 66}")
        
        print("\n" + "="*70)
        print("✅ Benchmark complete")
        print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="ACTP Benchmark - Compare with vs without ACTP packaging"
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Run all benchmarks (50, 100, 200 files)'
    )
    parser.add_argument(
        '--sizes', type=int, nargs='+', default=[100],
        help='Custom repo sizes to benchmark (default: 100)'
    )
    parser.add_argument(
        '--queries', type=int, default=5,
        help='Number of queries per benchmark (default: 5)'
    )
    
    args = parser.parse_args()
    
    sizes = [50, 100, 200] if args.all else args.sizes
    
    benchmark = ACTPBenchmark()
    results = benchmark.run(sizes=sizes, num_queries=args.queries)
    benchmark.print_report(results)


if __name__ == '__main__':
    main()
