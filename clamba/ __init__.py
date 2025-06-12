"""
CLAMBA - Smart Legal Contract Automaton Generator

A Python library for generating smart contract automatons from PDF contracts using AI.
"""

from .core.analyzer import CLAMBAAnalyzer
from .config.settings import CLAMBAConfig, load_config, create_sample_config
from .models.contract import Contract, ContractResult, ContractType, ContractStatus
from .models.process import Process, ProcessType
from .ai.factory import AIProviderFactory

__version__ = "0.1.0"
__author__ = "CLAMBA Team"
__email__ = "contact@clamba.ai"
__description__ = "Smart Legal Contract Automaton Generator using AI"

# Main exports
__all__ = [
    # Core functionality
    "CLAMBAAnalyzer",
    
    # Configuration
    "CLAMBAConfig",
    "load_config", 
    "create_sample_config",
    
    # Models
    "Contract",
    "ContractResult", 
    "ContractType",
    "ContractStatus",
    "Process",
    "ProcessType",
    
    # AI
    "AIProviderFactory",
    
    # Utilities
    "analyze_contract",
    "analyze_contracts_batch",
]


def analyze_contract(
    pdf_path: str,
    config_path: str = None,
    contract_type: ContractType = None,
    **kwargs
) -> ContractResult:
    """
    Quick function to analyze a single contract
    
    Args:
        pdf_path: Path to PDF contract
        config_path: Optional configuration file path
        contract_type: Optional contract type hint
        **kwargs: Additional arguments passed to analyzer
        
    Returns:
        ContractResult with generated automatons
        
    Example:
        >>> from clamba import analyze_contract, ContractType
        >>> result = analyze_contract("contract.pdf", contract_type=ContractType.LOGISTICS)
        >>> print(f"Generated {len(result.contract.automates)} automatons")
    """
    config = load_config(config_path)
    analyzer = CLAMBAAnalyzer(config)
    
    return analyzer.analyze_contract(
        pdf_path=pdf_path,
        contract_type=contract_type,
        **kwargs
    )


def analyze_contracts_batch(
    pdf_paths: list,
    output_dir: str,
    config_path: str = None,
    **kwargs
) -> list:
    """
    Quick function to analyze multiple contracts
    
    Args:
        pdf_paths: List of PDF file paths
        output_dir: Output directory for results
        config_path: Optional configuration file path
        **kwargs: Additional arguments passed to analyzer
        
    Returns:
        List of ContractResult objects
        
    Example:
        >>> from clamba import analyze_contracts_batch
        >>> results = analyze_contracts_batch(
        ...     ["contract1.pdf", "contract2.pdf"],
        ...     "./results/"
        ... )
        >>> print(f"Analyzed {len(results)} contracts")
    """
    config = load_config(config_path)
    analyzer = CLAMBAAnalyzer(config)
    
    return analyzer.analyze_multiple_contracts(
        pdf_paths=pdf_paths,
        output_dir=output_dir,
        **kwargs
    )


def get_version() -> str:
    """Get CLAMBA version"""
    return __version__


def get_supported_contract_types() -> list:
    """Get list of supported contract types"""
    return [ct for ct in ContractType if ct != ContractType.AUTO]


def get_available_ai_providers() -> list:
    """Get list of available AI providers"""
    return AIProviderFactory.get_available_providers()


# Package information
def get_info() -> dict:
    """Get package information"""
    return {
        "name": "clamba",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
        "supported_contract_types": [ct.value for ct in get_supported_contract_types()],
        "available_ai_providers": get_available_ai_providers(),
    }


# Version check for dependencies
def check_dependencies() -> dict:
    """
    Check availability of optional dependencies
    
    Returns:
        Dictionary with dependency status
    """
    dependencies = {
        "core": True,  # Always available
        "openai": False,
        "anthropic": False,
        "cli": False,
    }
    
    try:
        import openai
        dependencies["openai"] = True
    except ImportError:
        pass
    
    try:
        import anthropic
        dependencies["anthropic"] = True
    except ImportError:
        pass
    
    try:
        import typer
        import rich
        dependencies["cli"] = True
    except ImportError:
        pass
    
    return dependencies


# Initialize logging
def _setup_logging():
    """Setup basic logging configuration"""
    import logging
    
    # Create logger
    logger = logging.getLogger("clamba")
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set default level
        logger.setLevel(logging.INFO)


# Initialize on import
_setup_logging()


# Backward compatibility aliases
UniversalSmartLegalAnalyzer = CLAMBAAnalyzer  # For compatibility with original code