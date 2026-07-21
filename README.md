# ACTP - AI Context Transfer Protocol

Modeller arası taşınabilir **semantik bağlam** standardı. Claude'dan ChatGPT'ye, GPT'den başka bir modele — proje durumunu, kararları, açık soruları aktarın.

## 🎯 Temel Fark

**ACTP SADECİK dosya filtrelemesi DEĞİLDİR.**

- ❌ Diğer çözümler: "Binary dosyaları filtrele, cache'le, token kazan"
- ✅ ACTP: "Kararları, semantik katmanı, sözlüğü yakala — proje anlayışını aktarabilmen için"

## 📦 ACTP Paketi İçerir

### 1. **Temel İçerik**
- Kaynak dosyaları (filtrelenmiş)
- Checksum'lar (bütünlük doğrulaması)
- Metadata (kimlik, tarih, model bağlamı)

### 2. ⭐ **Semantik Katman** (ACTP'nin Kalbi)

#### Decisions (Kararlar)
```json
{
  "id": "db-choice",
  "title": "PostgreSQL seçtik",
  "description": "Veritabanı olarak PostgreSQL seçildi",
  "context": "Reliability ve ACID işlemleri lazımdı",
  "alternatives_considered": ["SQLite", "MongoDB", "MySQL"],
  "rationale": "PostgreSQL transaction support ve reliability'den ötürü",
  "date_made": "2026-07-15T10:00:00",
  "impact": "Sistem daha güvenilir ve stabil hale geldi"
}
