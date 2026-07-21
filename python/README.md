# ACTP Python Implementation

ACTP protokolünün Python referans uygulaması.

## Kurulum

```bash
git clone https://github.com/samiboran/actp-spec.git
cd actp-spec/python
pip install -e ".[dev]"
from actp.core.packager import ACTPPackager
from pathlib import Path

# Paket oluştur
packager = ACTPPackager("My Project", "1.0.0")

# Dosyaları ekle
for py_file in Path("src").glob("**/*.py"):
    packager.add_file_from_path(py_file)

# Karar ekle
packager.add_decision(
    id="db-choice",
    title="PostgreSQL seçtik",
    description="Veritabanı seçimi",
    context="Reliability lazım",
    alternatives=["SQLite", "MongoDB"],
    rationale="ACID support en iyisi"
)

# Paketi kaydet
packager.save_to_file(Path("project.actp"))
from actp.validator import ACTPValidator

validator = ACTPValidator()
is_valid, errors, warnings = validator.validate_file(Path("project.actp"))

if is_valid:
    print("✅ Paket geçerli!")
else:
    validator.print_report()
python/
├── actp/
│   ├── __init__.py
│   ├── core/
│   │   ├── schema.py       # Data classes
│   │   └── packager.py     # Packager
│   └── validator.py        # Validator
├── spec/
│   └── examples/
│       └── basic.actp      # Örnek paket
├── tests/
│   └── test_*.py
└── setup.py
Detaylı dokümantasyon için root README dosyasına bak.
