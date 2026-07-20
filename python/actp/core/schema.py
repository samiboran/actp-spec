import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import hashlib

try:
    import jsonschema
    from jsonschema import FormatChecker
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# ACTP v0.1.3 JSON Schema (inline, self-contained)
ACTP_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ACTP Package v0.1.3",
    "type": "object",
    "required": ["version", "project_name", "generated_at", "files", "metadata"],
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+$"
        },
        "project_name": {
            "type": "string",
            "minLength": 1
        },
        "generated_at": {
            "type": "string",
            "format": "date-time"
        },
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "content", "size", "type"],
                "properties": {
                    "path": {
                        "type": "string",
                        "pattern": r"^(?!.*\.\.)[^/\\][^\x00]*$",
                        "description": "Relative path, no .. segments, no absolute paths"
                    },
                    "content": {"type": "string"},
                    "size": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "type": {"type": "string"},
                    "sha256": {
                        "type": "string",
                        "pattern": r"^[a-f0-9]{64}$"
                    }
                }
            }
        },
        "metadata": {
            "type": "object",
            "required": ["total_files", "total_tokens_estimate"],
            "properties": {
                "total_files": {
                    "type": "integer",
                    "minimum": 0
                },
                "total_tokens_estimate": {
                    "type": "integer",
                    "minimum": 0
                },
                "excluded_dirs": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "warnings": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "generator": {"type": "string"}
            }
        }
    }
}


class ACTPValidator:
    """ACTP paketlerini schema ve checksum'e karsi dogrular."""

    def __init__(self):
        self.schema = ACTP_SCHEMA

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Schema dogrulama. (is_valid, errors) doner."""
        if not HAS_JSONSCHEMA:
            return False, ["jsonschema kutuphanesi kurulu degil"]

        try:
            jsonschema.validate(
                instance=data,
                schema=self.schema,
                format_checker=FormatChecker()
            )
            return True, []
        except jsonschema.ValidationError as e:
            return False, [f"Schema hatasi: {e.message} (konum: {list(e.path)})"]
        except Exception as e:
            return False, [f"Dogrulama basarisiz: {str(e)}"]

    def validate_checksums(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """SHA-256 checksum'lari content ile karsilastir."""
        errors = []

        for file_entry in data.get("files", []):
            if "sha256" not in file_entry:
                continue  # sha256 opsiyonel

            expected = file_entry["sha256"]
            actual = hashlib.sha256(
                file_entry["content"].encode("utf-8")
            ).hexdigest()

            if expected != actual:
                errors.append(
                    f"Checksum uyusmazligi ({file_entry['path']}): "
                    f"beklenen={expected}, gercek={actual}"
                )

        return len(errors) == 0, errors

    @staticmethod
    def is_safe_path(base_dir: Path, target_path: Path) -> bool:
        """
        Path traversal kontrolu: target_path, base_dir disina cikiyor mu?
        resolve() symlink'leri de takip eder, normalize eder.
        """
        try:
            base_resolved = base_dir.resolve()
            target_resolved = target_path.resolve()
            return str(target_resolved).startswith(str(base_resolved))
        except (OSError, RuntimeError):
            return False
