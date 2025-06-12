"""
CLAMBA - Smart Legal Contract Automaton Generator
"""

__version__ = "0.1.0"
__author__ = "CLAMBA Team"
__email__ = "contact@clamba.ai"
__description__ = "Smart Legal Contract Automaton Generator using AI"


def get_version():
    """Get CLAMBA version"""
    return __version__


def get_info():
    """Get package information"""
    return {
        "name": "clamba",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
    }


# Import des modules principaux avec gestion d'erreurs
try:
    from .config.settings import CLAMBAConfig, load_config, create_sample_config
    _CONFIG_AVAILABLE = True
except ImportError as e:
    _CONFIG_AVAILABLE = False
    print(f"Warning: Config not available: {e}")

try:
    from .models.process import Process, ProcessType
    from .models.contract import ContractType
    _MODELS_AVAILABLE = True
except ImportError as e:
    _MODELS_AVAILABLE = False
    print(f"Warning: Models not available: {e}")

try:
    from .core.analyzer import CLAMBAAnalyzer
    _ANALYZER_AVAILABLE = True
except ImportError as e:
    _ANALYZER_AVAILABLE = False
    print(f"Warning: Analyzer not available: {e}")

try:
    from .ai.factory import AIProviderFactory
    _AI_AVAILABLE = True
except ImportError as e:
    _AI_AVAILABLE = False
    print(f"Warning: AI factory not available: {e}")


def check_installation():
    """Check what's available"""
    return {
        "config": _CONFIG_AVAILABLE,
        "models": _MODELS_AVAILABLE, 
        "analyzer": _ANALYZER_AVAILABLE,
        "ai": _AI_AVAILABLE,
    }


# Exports de base (toujours disponibles)
__all__ = [
    "get_version",
    "get_info", 
    "check_installation",
]

# Exports conditionnels
if _CONFIG_AVAILABLE:
    __all__.extend(["CLAMBAConfig", "load_config", "create_sample_config"])

if _MODELS_AVAILABLE:
    __all__.extend(["Process", "ProcessType", "ContractType"])

if _ANALYZER_AVAILABLE:
    __all__.extend(["CLAMBAAnalyzer"])

if _AI_AVAILABLE:
    __all__.extend(["AIProviderFactory"])


def analyze_contract(pdf_path, **kwargs):
    """Quick analyze function"""
    if not _ANALYZER_AVAILABLE:
        raise ImportError("CLAMBAAnalyzer not available")
    
    config = load_config() if _CONFIG_AVAILABLE else None
    analyzer = CLAMBAAnalyzer(config)
    return analyzer.analyze_contract(pdf_path, **kwargs)


if _ANALYZER_AVAILABLE and _CONFIG_AVAILABLE:
    __all__.append("analyze_contract")