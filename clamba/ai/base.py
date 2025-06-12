"""
Base AI Provider interface for CLAMBA
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class AIConnectionError(AIProviderError):
    """Exception raised when AI provider connection fails"""
    pass


class AIRateLimitError(AIProviderError):
    """Exception raised when AI provider rate limit is exceeded"""
    pass


class AIResponseError(AIProviderError):
    """Exception raised when AI provider returns invalid response"""
    pass


class BaseAIProvider(ABC):
    """
    Abstract base class for AI providers
    
    All AI providers must implement this interface to be used with CLAMBA
    """

    def __init__(self, config: Any):
        """
        Initialize the AI provider
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config

    @abstractmethod
    def query(self, prompt: str, **kwargs) -> str:
        """
        Send a query to the AI provider
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            AI response as string
            
        Raises:
            AIProviderError: If the query fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the AI provider
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dictionary with model information
        """
        pass

    def get_provider_name(self) -> str:
        """
        Get the provider name
        
        Returns:
            Provider name as string
        """
        return self.__class__.__name__.replace("Provider", "").lower()

    def validate_response(self, response: str) -> bool:
        """
        Validate AI response
        
        Args:
            response: AI response to validate
            
        Returns:
            True if response is valid, False otherwise
        """
        return response is not None and response.strip() != ""

    def prepare_prompt(self, base_prompt: str, **context) -> str:
        """
        Prepare prompt with provider-specific formatting
        
        Args:
            base_prompt: Base prompt text
            **context: Additional context variables
            
        Returns:
            Formatted prompt
        """
        # Default implementation - can be overridden by providers
        return base_prompt

    def handle_error(self, error: Exception, context: Optional[str] = None) -> None:
        """
        Handle provider-specific errors
        
        Args:
            error: Original exception
            context: Optional context information
            
        Raises:
            AIProviderError: Appropriate provider error
        """
        if context:
            raise AIProviderError(f"{context}: {str(error)}") from error
        else:
            raise AIProviderError(str(error)) from error

    def get_retry_settings(self) -> Dict[str, Any]:
        """
        Get retry settings for this provider
        
        Returns:
            Dictionary with retry configuration
        """
        return {
            "max_retries": getattr(self.config, "max_retries", 3),
            "retry_delay": 1.0,
            "backoff_factor": 2.0,
        }

    def supports_streaming(self) -> bool:
        """
        Check if provider supports streaming responses
        
        Returns:
            True if streaming is supported, False otherwise
        """
        return False

    def get_token_limit(self) -> Optional[int]:
        """
        Get token limit for this provider/model
        
        Returns:
            Token limit or None if not applicable
        """
        return getattr(self.config, "max_tokens", None)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def truncate_text(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Truncate text to fit within token limits
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens (uses config default if None)
            
        Returns:
            Truncated text
        """
        if max_tokens is None:
            max_tokens = self.get_token_limit()
        
        if max_tokens is None:
            return text
        
        estimated_tokens = self.estimate_tokens(text)
        if estimated_tokens <= max_tokens:
            return text
        
        # Truncate to approximately max_tokens
        target_chars = max_tokens * 4
        return text[:target_chars] + "..."