# ACTP Örnekleri

Gerçek dünya kullanım örnekleri ve best practices.

---

## 📋 İçindekiler

1. [Örnek 1: Web Framework Projesi](#örnek-1-web-framework-projesi)
2. [Örnek 2: Python Kütüphanesi](#örnek-2-python-kütüphanesi)
3. [Örnek 3: Machine Learning Pipeline](#örnek-3-machine-learning-pipeline)
4. [Örnek 4: DevOps Altyapısı](#örnek-4-devops-altyapısı)
5. [Örnek 5: AI Agent Proje](#örnek-5-ai-agent-proje)

---

## Örnek 1: Web Framework Projesi

### Senaryo

React + TypeScript + Vite web framework'ü geliştiriyorsunuz.
Proje yapısı:

```
my-framework/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── utils/
│   └── types.ts
├── tests/
├── docs/
└── README.md
```

### ACTP Paketi Oluştur

```bash
actp pack ~/projects/my-framework \
  --name "React Framework" \
  --goal "Lightweight TypeScript-first React framework with excellent DX" \
  --depth 8 \
  --model claude \
  --created-by "alice@startup.com" \
  -o framework.actp
```

### Karar Tanımla (Python)

```python
from actp.core.packager import ACTPPackager
from pathlib import Path
import json

packager = ACTPPackager(
    project_name="React Framework",
    project_goal="Lightweight TypeScript-first React framework"
)

# Dosyalar ekle
for file_path in Path("src").rglob("*.tsx"):
    packager.add_file(file_path)

# 🔴 Kritik kararlar (P0 = LOCKED)
packager.add_decision(
    id="D1",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use TypeScript for 100% type coverage",
    rationale="Prevents bugs at compile time, improves IDE support, better refactoring",
    source_model="claude-3-sonnet"
)

packager.add_decision(
    id="D2",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use Vite as build tool",
    rationale="Faster dev server (ESM native), instant HMR, optimized production builds"
)

# 🟡 Yüksek öncelik (P1 = FLEXIBLE)
packager.add_decision(
    id="D3",
    priority="P1",
    certainty="HIGH",
    mutability="FLEXIBLE",
    content="Component-first architecture with strict separation of concerns",
    rationale="Enables reusability, improves testability, supports scaling"
)

packager.add_decision(
    id="D4",
    priority="P1",
    certainty="MEDIUM",
    mutability="FLEXIBLE",
    content="Implement custom hooks for state management",
    rationale="Lighter than Redux for small apps, better performance, simpler API"
)

# 🔵 Düşük öncelik (P2 = FLEXIBLE)
packager.add_decision(
    id="D5",
    priority="P2",
    certainty="LOW",
    mutability="FLEXIBLE",
    content="Support experimental CSS-in-JS approach",
    hallucination_risk=True,
    content="Consider supporting CSS Modules + Tailwind hybrid approach",
    rationale="Emerging pattern, needs validation in real projects"
)

# Sembol sözlüğü
packager.add_symbol("🔴", "Architecture decision, P0, locked")
packager.add_symbol("🟡", "Implementation strategy, P1, flexible")
packager.add_symbol("🔵", "Experimental, P2, low priority")
packager.add_symbol("🧪", "Needs testing")
packager.add_symbol("📚", "Documentation required")

# Görevler
packager.add_task("T1", "done", "Set up project structure with Vite", "🟢")
packager.add_task("T2", "done", "Create base component system", "🟢")
packager.add_task("T3", "pending", "Implement React hooks", "🟡")
packager.add_task("T4", "pending", "Write comprehensive test suite", "🧪")
packager.add_task("T5", "blocked", "Performance optimization", "🚨")

# Açık sorular
packager.add_open_question("Should we support Vue 3 / Svelte compatibility?")
packager.add_open_question("How to handle server-side rendering (SSR)?")
packager.add_open_question("What's our upgrade strategy for React major versions?")

# Sonraki adımlar
packager.add_next_step("Review and approve component API design")
packager.add_next_step("Set up CI/CD with GitHub Actions")
packager.add_next_step("Create comprehensive storybook for components")
packager.add_next_step("Benchmark performance against similar frameworks")

# Kaydet
packager.save_to_file(
    Path("framework.actp"),
    created_by="alice@startup.com",
    source_model="claude-3-sonnet"
)
```

### Paket İncele

```bash
actp inspect framework.actp
```

**Çıktı:**
```
📋 ACTP Package: framework.actp
============================================================

🎯 Project
   Name: React Framework
   Goal: Lightweight TypeScript-first React framework with excellent DX

📌 Decisions (5)
   [1] D1 (P0) - Use TypeScript for 100% type coverage...
   [2] D2 (P0) - Use Vite as build tool...
   [3] D3 (P1) - Component-first architecture...
   [4] D4 (P1) - Implement custom hooks for state management...
   [5] D5 (P2) - Support experimental CSS-in-JS approach...

✅ Tasks (5)
   [done] T1 - Set up project structure with Vite
   [done] T2 - Create base component system
   [pending] T3 - Implement React hooks
   [pending] T4 - Write comprehensive test suite
   [blocked] T5 - Performance optimization

❓ Open Questions (3)
   1. Should we support Vue 3 / Svelte compatibility?
   2. How to handle server-side rendering (SSR)?
   3. What's our upgrade strategy for React major versions?

➡️  Next Steps (4)
   1. Review and approve component API design
   2. Set up CI/CD with GitHub Actions
   3. Create comprehensive storybook for components
   4. Benchmark performance against similar frameworks

📊 Summary
   Symbol legend: 5
   Entity map: 0
   Priority matrix: 0
```

---

## Örnek 2: Python Kütüphanesi

### Senaryo

Veri işleme kütüphanesi `dataflow` geliştiriyorsunuz.

```
dataflow/
├── dataflow/
│   ├── core/
│   │   ├── pipeline.py
│   │   ├── executor.py
│   │   └── types.py
│   ├── processors/
│   │   ├── filter.py
│   │   ├── map.py
│   │   └── aggregate.py
│   └── __init__.py
├── tests/
├── docs/
└── setup.py
```

### Komut Satırı Kullanım

```bash
# Pakele
actp pack ./dataflow \
  --name "DataFlow" \
  --goal "Declarative data processing pipeline library with lazy evaluation" \
  --model claude \
  -o dataflow-context.actp

# Doğrula
actp validate dataflow-context.actp

# Özet oluştur
actp summarize dataflow-context.actp --format markdown > dataflow-summary.md

# Dışa aktar
actp export dataflow-context.actp --output-dir ./exported
```

### Exported Yapı

```
exported/
├── decisions.json      # Tüm tasarım kararları
├── tasks.json          # Proje görevleri
├── metadata.json       # Proje meta bilgileri
└── context.txt         # İnsan okunabilir özet
```

### Claude ile Kullan

```bash
# Paket kopyala
cat dataflow-context.actp | pbcopy

# Claude Chat'te:
# "İşte DataFlow Python kütüphanesi ACTP paketi: [yapıştır]
#  
#  Sorular:
#  1. D5 kararında bahsedilen "lazy evaluation" nasıl optimlendirilebilir?
#  2. T5 görevindeki "error handling" için hangi pattern önerirsiniz?
#  3. Açık sorular hakkında ne düşünüyorsunuz?"
```

---

## Örnek 3: Machine Learning Pipeline

### Senaryo

Görüntü sınıflandırması ML projesi.

```python
from actp.core.packager import ACTPPackager
from pathlib import Path

packager = ACTPPackager(
    project_name="ImageNet Classifier",
    project_goal="Efficient image classification model using vision transformers"
)

# DECISIONS

# 🔴 Model seçimi (LOCKED)
packager.add_decision(
    id="D1",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use Vision Transformer (ViT) instead of CNN",
    rationale="Superior accuracy on ImageNet, better transfer learning, attention mechanism captures global context",
    source_model="claude"
)

# 🔴 Framework seçimi
packager.add_decision(
    id="D2",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Implement in PyTorch with PyTorch Lightning",
    rationale="Production-ready, excellent GPU support, active research community"
)

# 🟡 Data augmentation
packager.add_decision(
    id="D3",
    priority="P1",
    certainty="MEDIUM",
    mutability="FLEXIBLE",
    content="Use AutoAugment + RandAugment for data augmentation",
    rationale="Reduces overfitting, improves generalization"
)

# 🟡 Optimizer seçimi
packager.add_decision(
    id="D4",
    priority="P1",
    certainty="HIGH",
    mutability="FLEXIBLE",
    content="Use AdamW optimizer with cosine annealing learning rate schedule",
    rationale="Converges faster than SGD, better generalization"
)

# 🔵 Speculative
packager.add_decision(
    id="D5",
    priority="P2",
    certainty="LOW",
    mutability="FLEXIBLE",
    hallucination_risk=True,
    content="Consider knowledge distillation from larger ViT model",
    rationale="Could improve accuracy with less compute",
    external_dependency=True
)

# TASKS

packager.add_task("T1", "done", "Setup PyTorch Lightning project", "🟢")
packager.add_task("T2", "done", "Implement data loader with ImageNet", "🟢")
packager.add_task("T3", "pending", "Implement ViT model architecture", "🟡")
packager.add_task("T4", "pending", "Train on GPU cluster", "🚀")
packager.add_task("T5", "pending", "Evaluation metrics and validation", "🧪")
packager.add_task("T6", "pending", "Deploy as TorchServe endpoint", "📦")

# SYMBOLS

packager.add_symbol("🤖", "ML/AI Decision")
packager.add_symbol("📊", "Data related")
packager.add_symbol("🚀", "Performance critical")
packager.add_symbol("🧪", "Needs validation")
packager.add_symbol("📦", "Deployment")

# QUESTIONS

packager.add_open_question("Should we ensemble with other ViT variants?")
packager.add_open_question("How to handle class imbalance in ImageNet?")
packager.add_open_question("What's our serving latency target?")

# NEXT STEPS

packager.add_next_step("Run hyperparameter search (learning rate, batch size)")
packager.add_next_step("Compare accuracy against baseline CNN model")
packager.add_next_step("Set up model versioning and experiment tracking (Weights & Biases)")
packager.add_next_step("Create inference pipeline for edge deployment")

packager.save_to_file(Path("ml_pipeline.actp"))
```

---

## Örnek 4: DevOps Altyapısı

### Senaryo

Kubernetes + Terraform altyapı projesi.

```python
from actp.core.packager import ACTPPackager
from pathlib import Path

packager = ACTPPackager(
    project_name="K8s-Infra",
    project_goal="Multi-region Kubernetes cluster with GitOps CD"
)

# INFRASTRUCTURE DECISIONS

packager.add_decision(
    id="D1",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use AWS EKS for managed Kubernetes",
    rationale="Enterprise-grade SLA, automatic patching, tight AWS integration"
)

packager.add_decision(
    id="D2",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Infrastructure as Code with Terraform",
    rationale="Version controlled, reproducible, state management"
)

packager.add_decision(
    id="D3",
    priority="P1",
    certainty="HIGH",
    mutability="FLEXIBLE",
    content="Use ArgoCD for GitOps continuous deployment",
    rationale="Git as single source of truth, declarative deployment"
)

packager.add_decision(
    id="D4",
    priority="P1",
    certainty="MEDIUM",
    mutability="FLEXIBLE",
    content="Implement Helm charts for application packaging",
    rationale="Standardized deployment, template reusability"
)

packager.add_decision(
    id="D5",
    priority="P1",
    certainty="HIGH",
    mutability="FLEXIBLE",
    content="Use Prometheus + Grafana for monitoring",
    rationale="Industry standard, Kubernetes native, rich visualization"
)

# NETWORK

packager.add_decision(
    id="D6",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use Calico for network policy enforcement",
    rationale="High performance, supports Kubernetes network policies"
)

# SECURITY

packager.add_decision(
    id="D7",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Enable pod security policies and RBAC",
    rationale="Essential for multi-tenant clusters, compliance requirements"
)

# BACKUP

packager.add_decision(
    id="D8",
    priority="P1",
    certainty="HIGH",
    mutability="FLEXIBLE",
    content="Use Velero for cluster backup and disaster recovery",
    rationale="Kubernetes-native backup, supports cross-region migration"
)

packager.save_to_file(Path("k8s_infra.actp"))
```

---

## Örnek 5: AI Agent Proje

### Senaryo

Autonomous AI agent geliştiriyorsunuz.

```python
from actp.core.packager import ACTPPackager
from pathlib import Path

packager = ACTPPackager(
    project_name="AutoResearch Agent",
    project_goal="Autonomous AI agent that researches topics and generates reports"
)

# AGENT ARCHITECTURE

packager.add_decision(
    id="D1",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Agent architecture: Perception → Planning → Action → Reflection",
    rationale="Proven agentic loop, supports long-horizon tasks, self-improvement"
)

packager.add_decision(
    id="D2",
    priority="P0",
    certainty="HIGH",
    mutability="LOCKED",
    content="Use Claude 3 Opus as base reasoning model",
    rationale="State-of-the-art reasoning, long context window (200K), excellent agentic capabilities"
)

packager.add_decision(
    id="D3",
    priority="P1",
    certainty="HIGH",
    mutability="FLEXIBLE",
    content="Implement tool use: web search, file read, API calls, code execution",
    rationale="Extends agent capabilities beyond training data"
)

packager.add_decision(
    id="D4",
    priority="P1",
    certainty="MEDIUM",
    mutability="FLEXIBLE",
    content="Store conversation history in vector database for few-shot learning",
    rationale="Improves performance over time, personalization"
)

packager.add_decision(
    id="D5",
    priority="P1",
    certainty="MEDIUM",
    mutability="FLEXIBLE",
    hallucination_risk=True,
    content="Implement self-correction mechanism with confidence scoring",
    rationale="Reduces errors, enables uncertainty handling"
)

packager.add_task("T1", "done", "Agent loop implementation", "🟢")
packager.add_task("T2", "done", "Tool registry and execution", "🟢")
packager.add_task("T3", "pending", "Web search tool integration", "🔧")
packager.add_task("T4", "pending", "Reflection and feedback mechanism", "🧠")
packager.add_task("T5", "pending", "Evaluation framework", "🧪")

packager.add_symbol("🔧", "Tool implementation")
packager.add_symbol("🧠", "Reasoning/Planning")
packager.add_symbol("🔄", "Feedback loop")

packager.add_open_question("How to prevent infinite loops in agent execution?")
packager.add_open_question("What's the optimal context length for planning?")
packager.add_open_question("How to measure agent alignment with human intent?")

packager.save_to_file(Path("ai_agent.actp"))
```

---

## Cross-Project Pattern

### Örnek: Monorepo Structure

```bash
# Monorepo yapısı
my-mono/
├── apps/
│   ├── web/
│   ├── api/
│   └── cli/
└── packages/
    ├── core/
    ├── ui/
    └── utils/

# Her alt-proje için ayrı ACTP oluştur
actp pack apps/web --name "Web App" -o packages/contexts/web.actp
actp pack apps/api --name "API Server" -o packages/contexts/api.actp
actp pack packages/core --name "Core Lib" -o packages/contexts/core.actp

# Veya ana ACTP
actp pack . --name "MyMono" --goal "Monorepo with 3 apps + 3 packages"
```

---

## Tips & Tricks

### 1️⃣ Paket Boyutunu Kontrol Et

```bash
# Dosya boyutunu görmek için
ls -lh *.actp

# JSON doğru formatlandığını kontrol et
python -m json.tool context.actp | head -20
```

### 2️⃣ Multiple Models İçin Export

```python
# Bir kez paket, her model için kullan
from pathlib import Path
import json

with open("context.actp") as f:
    packet = json.load(f)

# Claude'a gönder
print("1. Copy this for Claude:")
print(json.dumps(packet, indent=2)[:2000])  # İlk 2K char

# GPT'ye gönder
print("\n2. Copy this for GPT-4:")
print(json.dumps(packet, indent=2)[:2000])
```

### 3️⃣ Version Tracking

```bash
# Tarih bazlı versiyonlama
actp pack . -o context_$(date +%Y%m%d).actp

# Paket değişikliği takip et
diff context_20260721.actp context_20260722.actp
```

### 4️⃣ CI/CD Integration

```yaml
# GitHub Actions example
name: ACTP Context
on: [push]
jobs:
  pack:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install actp
      - run: actp pack . --name "CI Project" -o ci_context.actp
      - uses: actions/upload-artifact@v3
        with:
          name: actp-context
          path: ci_context.actp
```

---

## Sonraki Adımlar

✅ [GUIDE.md](GUIDE.md) — Detaylı API ve CLI kullanımı
✅ [Validator Kuralları](python/actp/validator.py) — Doğrulama şeması
✅ [Spec](actp.schema.json) — Tam JSON-LD spesifikasyonu

---

**Kendi örneğini mi eklemek istiyorsun?** [PR açmanızı bekliyoruz!](https://github.com/samiboran/actp-spec/pulls)
