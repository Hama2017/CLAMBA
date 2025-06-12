"""
AI Provider Factory for CLAMBA
"""

from typing import Union

from ..config.settings import CLAMBAConfig
from .base import BaseAIProvider
from .ollama import OllamaProvider


class AIProviderFactory:
    """Factory for creating AI providers"""

    @staticmethod
    def create_provider(config: CLAMBAConfig) -> BaseAIProvider:
        """
        Create an AI provider based on configuration
        
        Args:
            config: CLAMBA configuration
            
        Returns:
            AI provider instance
            
        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        provider_name = config.ai.provider.lower()
        
        if provider_name == "ollama":
            return OllamaProvider(config.ai.ollama)
        
        elif provider_name == "openai":
            try:
                from .openai import OpenAIProvider
                if config.ai.openai is None:
                    raise ValueError("OpenAI configuration is missing")
                return OpenAIProvider(config.ai.openai)
            except ImportError:
                raise ValueError(
                    "OpenAI provider requires 'openai' package. "
                    "Install with: pip install clamba[openai]"
                )
        
        elif provider_name == "anthropic":
            try:
                from .anthropic import AnthropicProvider
                if config.ai.anthropic is None:
                    raise ValueError("Anthropic configuration is missing")
                return AnthropicProvider(config.ai.anthropic)
            except ImportError:
                raise ValueError(
                    "Anthropic provider requires 'anthropic' package. "
                    "Install with: pip install clamba[anthropic]"
                )
        
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")

    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available AI providers"""
        providers = ["ollama"]
        
        try:
            import openai
            providers.append("openai")
        except ImportError:
            pass
        
        try:
            import anthropic
            providers.append("anthropic")
        except ImportError:
            pass
        
        return providers