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


def check_installation():
    """Check what's available"""
    status = {
        "core": True,
        "config": False,
        "models": False,
        "analyzer": False,
        "ai": False,
    }
    
    try:
        from .config.settings import CLAMBAConfig, load_config, create_sample_config
        status["config"] = True
        globals().update({
            "CLAMBAConfig": CLAMBAConfig,
            "load_config": load_config, 
            "create_sample_config": create_sample_config
        })
    except ImportError:
        pass
    
    try:
        from .models.process import Process, ProcessType
        from .models.contract import ContractType
        status["models"] = True
        globals().update({
            "Process": Process,
            "ProcessType": ProcessType,
            "ContractType": ContractType
        })
    except ImportError:
        pass
    
    try:
        from .core.analyzer import CLAMBAAnalyzer
        status["analyzer"] = True
        globals().update({"CLAMBAAnalyzer": CLAMBAAnalyzer})
    except ImportError:
        pass
    
    try:
        from .ai.factory import AIProviderFactory
        status["ai"] = True
        globals().update({"AIProviderFactory": AIProviderFactory})
    except ImportError:
        pass
    
    return status


# Imports automatiques au chargement du module
_status = check_installation()

# Exports de base (toujours disponibles)
__all__ = ["get_version", "get_info", "check_installation"]

# Ajout des exports conditionnels
if _status["config"]:
    __all__.extend(["CLAMBAConfig", "load_config", "create_sample_config"])

if _status["models"]:
    __all__.extend(["Process", "ProcessType", "ContractType"])

if _status["analyzer"]:
    __all__.extend(["CLAMBAAnalyzer"])

if _status["ai"]:
    __all__.extend(["AIProviderFactory"])


def analyze_contract(pdf_path, **kwargs):
    """Quick analyze function"""
    if not _status["analyzer"] or not _status["config"]:
        raise ImportError("CLAMBAAnalyzer or config not available")
    
    config = load_config()
    analyzer = CLAMBAAnalyzer(config)
    return analyzer.analyze_contract(pdf_path, **kwargs)


if _status["analyzer"] and _status["config"]:
    __all__.append("analyze_contract")

# Alias de compatibilité
if _status["analyzer"]:
    UniversalSmartLegalAnalyzer = CLAMBAAnalyzer
    __all__.append("UniversalSmartLegalAnalyzer")
