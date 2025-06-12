# Guide d'installation et de configuration CLAMBA

## 🚀 Installation rapide

### 1. Installation avec Poetry (recommandé)

```bash
# Cloner le projet
git clone https://github.com/votre-username/clamba.git
cd clamba

# Installer Poetry si pas encore installé
curl -sSL https://install.python-poetry.org | python3 -

# Installer les dépendances
poetry install

# Installation avec support OpenAI
poetry install --extras openai

# Installation complète avec tous les extras
poetry install --extras all
```

### 2. Installation avec pip

```bash
# Installation de base
pip install clamba

# Avec support OpenAI
pip install clamba[openai]

# Avec support Anthropic
pip install clamba[anthropic]

# Installation complète
pip install clamba[all]
```

## ⚙️ Configuration

### 1. Créer la configuration

```bash
# Créer un fichier de configuration d'exemple
clamba config-create

# Ou utiliser Poetry
poetry run clamba config-create
```

### 2. Configuration des fournisseurs IA

#### Ollama (local, recommandé pour débuter)

```bash
# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Démarrer le service
ollama serve

# Télécharger un modèle
ollama pull nous-hermes2
```

Configuration dans `clamba_config.yaml` :

```yaml
ai:
  provider: "ollama"
  ollama:
    url: "http://localhost:11434"
    model: "nous-hermes2"
```

#### OpenAI

```bash
# Définir la clé API
export OPENAI_API_KEY="your-api-key-here"
```

Configuration dans `clamba_config.yaml` :

```yaml
ai:
  provider: "openai"
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
```

#### Anthropic Claude

```bash
# Définir la clé API
export ANTHROPIC_API_KEY="your-api-key-here"
```

Configuration dans `clamba_config.yaml` :

```yaml
ai:
  provider: "anthropic"
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet-20240229"
```

### 3. Valider la configuration

```bash
# Valider la configuration
clamba config-validate

# Ou avec Poetry
poetry run clamba config-validate
```

## 🧪 Test d'installation

### 1. Test rapide

```bash
# Afficher les informations
clamba info

# Ou avec Poetry
poetry run clamba info
```

### 2. Test avec un contrat

```python
# test_installation.py
from clamba import analyze_contract, ContractType

# Test avec un PDF de contrat
result = analyze_contract(
    "exemple_contrat.pdf",
    contract_type=ContractType.LOGISTICS
)

print(f"✅ Analyse réussie : {len(result.contract.automates)} automates générés")
```

```bash
# Exécuter le test
python test_installation.py

# Ou avec Poetry
poetry run python test_installation.py
```

## 🔧 Développement

### Configuration de l'environnement de développement

```bash
# Cloner et configurer
git clone https://github.com/votre-username/clamba.git
cd clamba

# Installer avec dépendances de développement
poetry install --with dev

# Installer les hooks pre-commit
poetry run pre-commit install

# Lancer les tests
poetry run pytest

# Formater le code
poetry run black clamba/
poetry run isort clamba/

# Vérifier la qualité du code
poetry run flake8 clamba/
poetry run mypy clamba/
```

### Structure du projet

```
clamba/
├── clamba/                 # Code source principal
│   ├── __init__.py        # Point d'entrée
│   ├── core/              # Logique métier
│   ├── ai/                # Fournisseurs IA
│   ├── models/            # Modèles de données
│   ├── utils/             # Utilitaires
│   ├── config/            # Configuration
│   └── cli.py             # Interface CLI
├── tests/                 # Tests
├── docs/                  # Documentation
├── examples/              # Exemples d'utilisation
├── pyproject.toml         # Configuration Poetry
├── README.md              # Documentation principale
└── clamba_config.yaml     # Configuration d'exemple
```

## 🚨 Résolution des problèmes

### Problème : Ollama non accessible

```bash
# Vérifier si Ollama fonctionne
curl http://localhost:11434/api/tags

# Redémarrer Ollama
ollama serve

# Vérifier les modèles installés
ollama list
```

### Problème : Erreur de clé API OpenAI/Anthropic

```bash
# Vérifier les variables d'environnement
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Définir les clés dans .env
cat > .env << EOF
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
EOF
```

### Problème : Dépendances manquantes

```bash
# Réinstaller les dépendances
poetry install --extras all

# Ou avec pip
pip install clamba[all]
```

### Problème : Erreur de PDF

```bash
# Vérifier le fichier PDF
file votre_contrat.pdf

# Installer des dépendances PDF supplémentaires si nécessaire
pip install pdfplumber pypdf2
```

## 📚 Ressources supplémentaires

- **Documentation complète** : [docs/](./docs/)
- **Exemples** : [examples/](./examples/)
- **Tests** : [tests/](./tests/)
- **Issues** : [GitHub Issues](https://github.com/votre-username/clamba/issues)

## 🤝 Contribution

Voir [CONTRIBUTING.md](./CONTRIBUTING.md) pour les guidelines de contribution.

## 📄 Licence

Ce projet est sous licence MIT - voir [LICENSE](./LICENSE) pour les détails.