# CLAMBA - Smart Legal Contract Automaton Generator 🤖⚖️

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

**CLAMBA** (Contract Legal Automaton with Modular Business Analysis) est une bibliothèque Python qui génère automatiquement des automates de contrats intelligents à partir de documents PDF en utilisant l'intelligence artificielle.

## 🚀 Fonctionnalités

- **Analyse universelle** : Compatible avec tous types de contrats (logistique, vente, prestation, immobilier, etc.)
- **Multi-modèles IA** : Support d'Ollama, OpenAI GPT, Claude Anthropic
- **Génération d'automates** : Création automatique d'automates d'états finis
- **Détection de dépendances** : Analyse intelligente des processus métier
- **IDs sanitized** : Génération d'identifiants propres sans accents
- **Configuration flexible** : Fichier de configuration simple
- **CLI intégrée** : Interface en ligne de commande

## 📦 Installation

### Via Poetry (recommandé)

```bash
# Installation de base
poetry add clamba

# Avec support OpenAI
poetry add clamba[openai]

# Avec support Anthropic Claude
poetry add clamba[anthropic]

# Installation complète avec CLI
poetry add clamba[all]
```

### Via pip

```bash
# Installation de base
pip install clamba

# Installation complète
pip install clamba[all]
```

## ⚙️ Configuration

### 1. Fichier de configuration

Créez un fichier `clamba_config.yaml` dans votre projet :

```yaml
# Configuration CLAMBA
ai:
  # Modèle IA à utiliser : "ollama", "openai", "anthropic"
  provider: "ollama"
  
  # Configuration Ollama (local)
  ollama:
    url: "http://localhost:11434"
    model: "nous-hermes2"
    max_tokens: 4000
    temperature: 0.05
    
  # Configuration OpenAI
  openai:
    api_key: "${OPENAI_API_KEY}"  # Ou directement la clé
    model: "gpt-4"
    max_tokens: 4000
    temperature: 0.05
    
  # Configuration Anthropic Claude
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"  # Ou directement la clé
    model: "claude-3-sonnet-20240229"
    max_tokens: 4000
    temperature: 0.05

# Configuration de l'analyse
analysis:
  max_retries: 3
  min_processes: 3
  max_processes: 6
  max_steps_per_process: 7

# Configuration de sortie
output:
  include_metadata: true
  sanitize_ids: true
  output_format: "json"  # "json" ou "yaml"
```

### 2. Variables d'environnement

Créez un fichier `.env` :

```bash
# Clés API (optionnel si dans le config)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configuration CLAMBA
CLAMBA_CONFIG_PATH=./clamba_config.yaml
CLAMBA_DEBUG=false
```

## 🔧 Utilisation

### Interface Python

```python
from clamba import CLAMBAAnalyzer
from clamba.config import CLAMBAConfig

# Chargement de la configuration
config = CLAMBAConfig.from_file("clamba_config.yaml")

# Initialisation de l'analyseur
analyzer = CLAMBAAnalyzer(config)

# Analyse d'un contrat PDF
result = analyzer.analyze_contract("contrat.pdf")

# Sauvegarde du résultat
analyzer.save_result(result, "smart_contract.json")

print(f"✅ Analyse terminée : {len(result.automates)} automates générés")
```

### Interface CLI

```bash
# Analyse basique
clamba analyze contrat.pdf

# Avec configuration personnalisée
clamba analyze contrat.pdf --config my_config.yaml

# Avec modèle spécifique
clamba analyze contrat.pdf --provider openai --model gpt-4

# Avec sortie personnalisée
clamba analyze contrat.pdf --output smart_contract.json --format yaml

# Mode debug
clamba analyze contrat.pdf --debug
```

### Exemple avancé

```python
from clamba import CLAMBAAnalyzer
from clamba.models import ContractType
from clamba.config import AIProvider, CLAMBAConfig

# Configuration programmatique
config = CLAMBAConfig(
    ai=AIProvider(
        provider="openai",
        openai={
            "api_key": "your-key",
            "model": "gpt-4",
            "temperature": 0.1
        }
    )
)

# Analyse avec métadonnées spécifiques
analyzer = CLAMBAAnalyzer(config)
result = analyzer.analyze_contract(
    pdf_path="contrat_complexe.pdf",
    contract_type=ContractType.LOGISTICS,
    custom_instructions="Focalisez sur les processus douaniers"
)

# Accès aux résultats détaillés
for automate in result.automates:
    print(f"Automate: {automate.name}")
    print(f"États: {len(automate.states)}")
    print(f"Transitions: {len(automate.transitions)}")
    
    if automate.dependencies:
        deps = [dep.name for dep in automate.dependencies]
        print(f"Dépendances: {', '.join(deps)}")
```

## 🏗️ Architecture

```
clamba/
├── __init__.py              # Point d'entrée principal
├── core/                    # Cœur de l'analyse
│   ├── analyzer.py         # Analyseur principal
│   ├── pdf_extractor.py    # Extraction PDF
│   └── process_detector.py # Détection de processus
├── ai/                     # Interfaces IA
│   ├── base.py            # Interface de base
│   ├── ollama.py          # Provider Ollama
│   ├── openai.py          # Provider OpenAI
│   └── anthropic.py       # Provider Anthropic
├── models/                 # Modèles de données
│   ├── contract.py        # Modèles de contrat
│   ├── automate.py        # Modèles d'automate
│   └── process.py         # Modèles de processus
├── utils/                  # Utilitaires
│   ├── sanitizer.py       # Sanitization des IDs
│   ├── validator.py       # Validation des données
│   └── json_parser.py     # Parsing JSON robuste
├── config/                 # Configuration
│   └── settings.py        # Gestion de la configuration
└── cli.py                 # Interface CLI
```

## 🧪 Tests

```bash
# Lancer tous les tests
poetry run pytest

# Tests avec couverture
poetry run pytest --cov=clamba

# Tests d'intégration
poetry run pytest tests/integration/

# Test sur un contrat spécifique
poetry run pytest tests/test_analyzer.py::test_logistics_contract
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche feature (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add amazing feature'`)
4. Push sur la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

### Configuration de développement

```bash
# Cloner le projet
git clone https://github.com/yourusername/clamba.git
cd clamba

# Installer les dépendances de développement
poetry install --with dev

# Installer les hooks pre-commit
poetry run pre-commit install

# Lancer les tests
poetry run pytest

# Formater le code
poetry run black clamba/
poetry run isort clamba/
```

## 📝 Exemples de contrats supportés

- **Contrats logistiques** : Transport, manutention, stockage
- **Contrats de vente** : B2B, B2C, vente en ligne
- **Contrats de prestation** : Services, consulting, maintenance
- **Contrats immobiliers** : Location, vente, gestion
- **Contrats de travail** : CDI, CDD, freelance
- **Contrats commerciaux** : Partenariat, distribution, franchise

## 🔍 Exemple de sortie

```json
{
  "id": "contract-ai-20240612143022",
  "name": "CONTRAT DE PRESTATION DE SERVICE",
  "status": "draft",
  "description": "Contrat généré automatiquement par IA PURE - 4 automates détectés",
  "automates": [
    {
      "id": "processus-qualification-besoin",
      "name": "Processus de qualification du besoin",
      "active": false,
      "states": [...],
      "transitions": [...],
      "automataDependencies": []
    }
  ]
}
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/yourusername/clamba/issues)
- **Discussions** : [GitHub Discussions](https://github.com/yourusername/clamba/discussions)
- **Email** : support@clamba.ai

## 🙏 Remerciements

- [Ollama](https://ollama.ai) pour l'IA locale
- [OpenAI](https://openai.com) pour GPT
- [Anthropic](https://anthropic.com) pour Claude
- [Poetry](https://python-poetry.org) pour la gestion des dépendances