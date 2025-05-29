# 🤖 CLAMBA

**CLAMBA** (CLAude + MAxence + BA) est une bibliothèque Python intelligente qui génère automatiquement des fichiers `.slca` (Smart Legal Contract Automaton) à partir de contrats en PDF.

💡 Idéal pour les projets de Smart Legal Contracts comme SLC + MSFSM.

---

## 🚀 Fonctionnalités

- 📄 Extraction de texte à partir de fichiers PDF
- 🧠 Génération automatique d’un automate `.slca` via un LLM (ex : Mistral avec Ollama)
- ⚙️ Configurable via un fichier JSON (`clamba.config.json`)
- ✅ Validation du fichier `.slca`
- 🐳 Docker-ready

---

## 📦 Installation (locale)

```bash
git clone https://github.com/ton-org/clamba.git
cd clamba
pip install -e .
```

---

## ⚙️ Exemple d’utilisation

```python
from clamba.core import generate_slca_from_pdf

slca = generate_slca_from_pdf("contrat.pdf", config_path="clamba.config.json")
print(slca)
```

---

## 🔧 Exemple de config (`clamba.config.json`)

```json
{
  "llm_provider": "ollama",
  "llm_endpoint": "http://localhost:11434/api/generate",
  "model_name": "mistral",
  "temperature": 0.3,
  "max_tokens": 1000
}
```

---

## 🐳 Utilisation avec Docker

### Construction

```bash
docker build -t clamba .
```

### Lancement

```bash
docker run -p 8000:8000 -v $(pwd):/app clamba
```

### API disponible

```http
POST /generate-slca
Content-Type: multipart/form-data
Body: file=@mon_contrat.pdf
```

---

## 🧠 Roadmap (v0.2+)

- [ ] Support des prompts multi-langues
- [ ] Intégration directe de Mistral local via `llama-cpp-python`
- [ ] Validation graphique de l’automate

---

## 👨‍💻 Auteur

**Hamadou Ba** – en collaboration avec Claude Duvallet & Maxence Lambard  
Projet réalisé au LITIS – Université Le Havre  
Licence : MIT
