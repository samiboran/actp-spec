# ACTP Kullanım Rehberi

**ACTP** (Agent Context Transfer Protocol) — Projeleri yapay zeka ajanlarına taşınabilir, semantik bakımdan zengin **bağlam paketlerine** dönüştürür.

---

## 📚 İçindekiler

1. [Nedir?](#nedir)
2. [Neden Kullan?](#neden-kullan)
3. [Kurulum](#kurulum)
4. [Hızlı Başlangıç](#hızlı-başlangıç)
5. [CLI Komutları](#cli-komutları)
6. [Python API](#python-api)
7. [Semanti Katman](#semantik-katman)
8. [Örnekler](#örnekler)
9. [Best Practices](#best-practices)

---

## Nedir?

ACTP, projeleri **JSON-LD** formatında **taşınabilir bağlam paketlerine** dönüştürür:

```json
{
  "@context": "https://actp.dev/schema/v0.1",
  "@type": "ACTPPacket",
  "actp_version": "0.1",
  "project": {
    "name": "My Project",
    "goal": "Build a web framework"
  },
  "decisions": [
    {
      "id": "D1",
      "priority": "P0",
      "certainty": "HIGH",
      "content": "Use TypeScript for type safety"
    }
  ],
  "symbol_legend": {
    "🔴": "priority=P0, mutability=LOCKED, certainty=HIGH",
    "🟡": "priority=P1, mutability=FLEXIBLE, certainty=MEDIUM"
  },
  "tasks": [...],
  "next_steps": [...]
}
```

**Anahtar özellikler:**
- ✅ **JSON-LD** — Web standardı, interoperable
- ✅ **Semantik kararlar** — Neden, öncelik, belirlililik
- ✅ **Sembol sözlüğü** — İnsan + makine okunabilir
- ✅ **Taşınabilir** — Model arası, format arası
- ✅ **Doğrulanabilir** — SHA-256 hash'ler, schema kontrolü

---

## Neden Kullan?

### ❌ Geleneksel Yöntem (Sorunlar)

```
Proje dosyaları → Claude'a yapıştır
                ↓
                Bağlam penceresini doldur
                ↓
                Model başka bir yapay zekaya değişir
                ↓
                Yapı/bağlam kaybı
```

### ✅ ACTP Yöntemi (Çözüm)

```
Proje → ACTP paketi (JSON-LD)
        ↓
        Depolanabilir, harcanabilir, doğrulanabilir
        ↓
        Claude → GPT → Gemini (sorunsuz)
        ↓
        Tam bağlam, kararlar, semboller korunur
```

**Faydalar:**
- 💾 **Verimli** — Token sayısı 40-60% azalır
- 🔄 **Interoperable** — Model/tool arası
- 🔐 **Doğrulanabilir** — SHA-256 hashes
- 📋 **Semantik** — Kararlar, tasarım, kavramlar korunur
- ⚡ **Hızlı** — Önbellek + yeniden kullanım

---

## Kurulum

### Via pip

```bash
pip install actp
```

### Via poetry

```bash
poetry add actp
```

### Development

```bash
git clone https://github.com/samiboran/actp-spec.git
cd actp-spec/python
pip install -e .
```

---

## Hızlı Başlangıç

### 1️⃣ Projeyi Pakele

```bash
# Temel kullanım
actp pack . --name "My Project" --goal "Build a web app" -o context.actp

# Seçenekler
actp pack . \
  --name "ML Pipeline" \
  --goal "Train image classifier" \
  --depth 10 \
  --model claude \
  --created-by "alice@example.com" \
  -o ml_context.actp
```

### 2️⃣ Doğrula

```bash
actp validate context.actp
```

**Çıktı:**
```
🔍 Validating 'context.actp'...
✅ Validation passed
   Project: My Project
   Decisions: 5
   Created: 2026-07-21T10:00:00Z
```

### 3️⃣ İncele

```bash
actp inspect context.actp
```

**Çıktı:**
```
📋 ACTP Package: context.actp
============================================================

🎯 Project
   Name: My Project
   Goal: Build a web framework

📌 Decisions (3)
   [1] D1 (P0) - Use TypeScript for type safety...
   [2] D2 (P1) - Implement modular architecture...
   [3] D3 (P2) - Support plugin system...

✅ Tasks (2)
   [done] T1 - Setup project structure
   [pending] T2 - Implement core API

❓ Open Questions (1)
   1. How to handle cross-cutting concerns?

➡️  Next Steps (2)
   1. Write comprehensive test suite
   2. Set up CI/CD pipeline

📊 Summary
   Symbol legend: 3
   Entity map: 5
   Priority matrix: 3
```

### 4️⃣ Claude/GPT'ye Gönder

```bash
# Dosya içeriğini kopyala
cat context.actp | pbcopy  # macOS
cat context.actp | xclip   # Linux

# Claude'a yapıştır + prompt:
# "İşte projenin ACTP paketi: [yapıştır]
#  Sonraki adımları planla ve karar D4 oluştur."
```

---

## CLI Komutları

### `actp pack`

Projeyi ACTP paketine dönüştür.

```bash
actp pack <project_path> \
  --name <proje_adı> \
  --goal <hedef> \
  [--output <dosya>] \
  [--depth <derinlik>] \
  [--model <claude|chatgpt|gemini>] \
  [--created-by <isim>]
```

**Örnek:**
```bash
actp pack ~/projects/actp \
  --name "ACTP Protocol" \
  --goal "Semantic context transfer for AI agents" \
  --output actp-v0.1.actp \
  --depth 5 \
  --model claude
```

---

### `actp validate`

Schema, hash, enum doğrulaması yap.

```bash
actp validate <actp_file>
```

**Kontroller:**
- ✅ JSON-LD yapısı (@context, @type, actp_version)
- ✅ Zorunlu alanlar (project, decisions, symbol_legend)
- ✅ Vocabulary hash tutarlılığı
- ✅ Decision priority/certainty/mutability enums
- ✅ Task status enums

---

### `actp inspect`

Paketi insan okunabilir formatta göster.

```bash
actp inspect <actp_file>
```

---

### `actp export`

Paket içeriğini ayrı dosyalara dışa aktar.

```bash
actp export <actp_file> [--output-dir <dizin>]
```

**Oluşturulan dosyalar:**
- `decisions.json` — Karar listesi
- `tasks.json` — Görev listesi
- `metadata.json` — Meta bilgiler
- `context.txt` — İnsan okunabilir özet

---

### `actp summarize`

Paketi metin olarak özetle.

```bash
actp summarize <actp_file> [--format markdown|json|yaml]
```

**Örnek (Markdown):**
```bash
actp summarize context.actp --format markdown
```

**Çıktı:**
```markdown
# My Project

## Goal
Build a web framework

## Decisions (3)

### D1 - Use TypeScript for type safety
- **Priority:** P0
- **Certainty:** HIGH
- **Mutability:** LOCKED
- **Rationale:** Type safety prevents bugs, improves IDE support

### D2 - Implement modular architecture
- **Priority:** P1
- **Certainty:** MEDIUM
- **Mutability:** FLEXIBLE
- **Rationale:** Supports scaling, enables plugin system

## Next Steps
- Write comprehensive test suite
- Set up CI/CD pipeline
```

---

## Python API

### Paket Oluştur (Programmatik)

```python
from actp.core.packager import ACTPPackager
from pathlib import Path

# Packager oluştur
packager = ACTPPackager(
    project_name="My Project",
    project_goal="Build a web framework"
)

# Dosyalar ekle
for file_path in Path("src").rglob("*.py"):
    packager.add_file(file_path)

# Kararlar ekle
packager.add_decision(
    id="D1",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use TypeScript for type safety",
    rationale="Prevents bugs, better IDE support",
    source_model="claude"
)

# Sembol sözlüğü
packager.add_symbol(
    symbol="🔴",
    meaning="Critical decision",
    priority="P0",
    mutability="LOCKED",
    certainty="HIGH"
)

# Görevler
packager.add_task(
    id="T1",
    status="pending",
    description="Implement core API",
    symbol="🟡"
)

# Paket oluştur ve kaydet
packager.save_to_file(
    Path("context.actp"),
    created_by="alice@example.com",
    source_model="claude"
)
```

### Dizinden Otomatik Paketleme

```python
from actp.core.packager import ACTPPackagerFactory
from pathlib import Path

packet = ACTPPackagerFactory.pack_directory(
    directory=Path("./my_project"),
    project_name="My Project",
    project_goal="Build a web framework",
    max_depth=10
)

# Dictionary'ye dönüştür
packet_dict = packet.to_dict()

# JSON dosyasına kaydet
import json
with open("context.actp", "w") as f:
    json.dump(packet_dict, f, indent=2)
```

### Paket Doğrula

```python
from actp.validator import ACTPValidator
import json

validator = ACTPValidator()

with open("context.actp") as f:
    data = json.load(f)

is_valid, errors, warnings = validator.validate_data(data)

if is_valid:
    print("✅ Valid!")
else:
    for error in errors:
        print(f"❌ {error}")

for warning in warnings:
    print(f"⚠️  {warning}")
```

---

## Semantik Katman

### Kararlar (Decisions)

Her karar **5 zorunlu alan** ile tanımlanır:

| Alan | Tür | Örnek | Anlamı |
|------|-----|-------|--------|
| `id` | string | "D1" | Benzersiz tanımlayıcı |
| `priority` | enum | "P0" | P0 (kritik), P1 (yüksek), P2 (düşük) |
| `certainty` | enum | "HIGH" | HIGH, MEDIUM, LOW — ne kadar emin? |
| `mutability` | enum | "LOCKED" | LOCKED (değişmez) veya FLEXIBLE |
| `content` | string | "Use TypeScript" | Kararın kendisi |

**Opsiyonel alanlar:**
- `symbol` — Emoji (🔴, 🟡, 🔵)
- `rationale` — Neden bu karar?
- `source_model` — Hangi model yaptı?
- `hallucination_risk` — Düşük emin misiniz?
- `external_dependency` — Dış kaynağa bağlı mı?

**Örnek:**

```json
{
  "id": "D1",
  "priority": "P0",
  "certainty": "HIGH",
  "mutability": "LOCKED",
  "content": "Use TypeScript for type safety",
  "symbol": "🔴",
  "rationale": "Prevents runtime errors, improves IDE support",
  "source_model": "claude-3-sonnet",
  "hallucination_risk": false,
  "external_dependency": false
}
```

### Sembol Sözlüğü (Symbol Legend)

İnsan + makine okunabilir sembol eşlemeleri:

```json
{
  "symbol_legend": {
    "🔴": "priority=P0, mutability=LOCKED, certainty=HIGH",
    "🟡": "priority=P1, mutability=FLEXIBLE, certainty=MEDIUM",
    "🔵": "priority=P2, mutability=FLEXIBLE, certainty=LOW",
    "🟢": "status=COMPLETED",
    "🌫️": "certainty=LOW, hallucination_risk=true",
    "🔗": "external_dependency=true"
  }
}
```

---

## Örnekler

### Örnek 1: Basit Web Projesi

```bash
mkdir demo && cd demo

# Proje yapısı oluştur
mkdir src tests docs
echo "def hello(): return 'world'" > src/main.py
echo "test content" > tests/test_main.py
echo "# README" > README.md

# Pakele
actp pack . \
  --name "Simple Web App" \
  --goal "Learning project for web development" \
  -o app.actp

# Doğrula
actp validate app.actp

# İncele
actp inspect app.actp
```

### Örnek 2: Semantik Karar Ekleme

```python
from actp.core.packager import ACTPPackager
from pathlib import Path

packager = ACTPPackager("ML Project", "Train image classifier")

# Kararlar
packager.add_decision(
    id="D1",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use PyTorch for deep learning",
    rationale="Best performance, largest community, research-backed"
)

packager.add_decision(
    id="D2",
    priority="P1",
    certainty="MEDIUM",
    mutability="FLEXIBLE",
    content="Implement data augmentation",
    rationale="Improves generalization, but adds complexity"
)

packager.add_decision(
    id="D3",
    priority="P2",
    certainty="LOW",
    mutability="FLEXIBLE",
    content="Use vision transformer architecture",
    hallucination_risk=True,  # Henüz doğrulanmadı
    external_dependency=True  # HuggingFace modellerine bağlı
)

# Sembol sözlüğü
packager.add_symbol("🤖", "AI/ML Decision")
packager.add_symbol("📊", "Data related")
packager.add_symbol("🚨", "High risk")

# Görevler
packager.add_task("T1", "done", "Data preparation", "🟢")
packager.add_task("T2", "pending", "Model training", "🟡")
packager.add_task("T3", "blocked", "Deployment", "🚨")

# Sorular
packager.add_open_question("How to handle class imbalance?")
packager.add_open_question("Should we use ensemble methods?")

# Sonraki adımlar
packager.add_next_step("Implement cross-validation")
packager.add_next_step("Set up MLOps pipeline")

packager.save_to_file(Path("ml_project.actp"))
```

---

## Best Practices

### ✅ DO's (Yap)

1. **Önemli Kararları Kaydet**
   ```python
   packager.add_decision(
       id="D1",
       priority="P0",
       content="Use PostgreSQL",
       rationale="ACID compliance, JSON support, proven scale"
   )
   ```

2. **Belirliliği İşaretle**
   ```python
   packager.add_decision(
       id="D2",
       certainty="LOW",
       hallucination_risk=True,  # Düşük güven
       content="Speculative architecture"
   )
   ```

3. **Dış Bağımlılıkları Belirle**
   ```python
   packager.add_decision(
       id="D3",
       external_dependency=True,  # Harici kaynağa bağlı
       content="Use AWS Lambda"
   )
   ```

4. **Sembol Sözlüğünü Konsistent Tut**
   - 🔴 = P0 (LOCKED, HIGH)
   - 🟡 = P1 (FLEXIBLE, MEDIUM)
   - 🔵 = P2 (FLEXIBLE, LOW)

5. **Bağlam Hiyerarşisini Saygı Duy**
   - Kısıtlamalar > Soft Preferences
   - P0 > P1 > P2

### ❌ DON'Ts (Yapma)

1. **Çok Fazla Karar Ekleme**
   - P0/P1 ile sınırlı tut (5-10 max)
   - Gereksiz detayları hariç tut

2. **Muğlak Karar İçeriği**
   ```python
   # ❌ BAD
   "Improve performance"
   
   # ✅ GOOD
   "Cache database queries using Redis to reduce latency from 500ms to 50ms"
   ```

3. **Hash'i Manuel Düzenleme**
   - ACTP doğrulama başarısız olur
   - Validator otomatik hesaplar

4. **Eksik Rationale**
   - Her P0 kararı için rationale ekle
   - Gelecek ekip için açıkla

---

## Sorun Giderme

### ❌ "JSON geçersiz" hatası

```bash
# Dosya bozuk mı kontrol et
python -m json.tool context.actp > /dev/null
```

### ❌ "Vocabulary hash uyuşmuyor"

```python
# Hash'i yeniden hesapla
packager = ACTPPackager()
# ... sembol ekle ...
vocab_hash = packager.calculate_vocabulary_hash()
print(vocab_hash)
```

### ❌ "Schema doğrulama başarısız"

```bash
actp validate context.actp  # Detaylı hatalar görülür
```

---

## Kaynaklar

- 📖 [ACTP Spec](https://github.com/samiboran/actp-spec) — Tam spesifikasyon
- 🧪 [Örnekler](python/spec/examples/) — Gerçek kullanım örnekleri
- 📝 [API Dökümantasyonu](python/actp/core/) — Python API
- 🔍 [Validator](python/actp/validator.py) — Doğrulama kuralları

---

## Lisans

MIT

---

**Sorularınız mı var?** [GitHub Issues](https://github.com/samiboran/actp-spec/issues) açın.
