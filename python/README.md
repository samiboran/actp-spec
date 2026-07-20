ACTP - Agent Context Transfer Protocol
ACTP, projelerinizi AI asistanlarla paylaşmak için optimize edilmiş bir paketleme formatıdır.
Kurulum
bash
pip install -e .
# veya tüm özelliklerle:
pip install -e ".[all]"
Kullanım
Paketleme
bash
actp pack ./my-project -o context.actp --depth 3
Paketi Açma
bash
actp unpack context.actp -o ./output
Paket İnceleme
bash
actp inspect context.actp
Doğrulama
bash
actp validate context.actp --checksums
Özellikler
✅ JSON Schema doğrulama
✅ SHA-256 checksum
✅ Path traversal koruması
✅ Secret taraması (API key'ler vb.)
✅ .gitignore desteği
✅ Binary dosya filtreleme
✅ Dosya boyutu limiti (10MB)