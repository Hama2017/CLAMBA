"""
OpenAI AI Provider for CLAMBA
"""

import time
from typing import Any, Dict, Optional

from ..config.settings import OpenAIConfig
from ..utils.logger import get_logger
from .base import (
    AIConnectionError,
    AIProviderError,
    AIRateLimitError,
    AIResponseError,
    BaseAIProvider,
)

try:
    import openai
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "OpenAI provider requires 'openai' package. "
        "Install with: pip install clamba[openai]"
    )


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI provider for GPT models
    
    Supports GPT-3.5, GPT-4, and other OpenAI models
    """

    def __init__(self, config: OpenAIConfig):
        """
        Initialize OpenAI provider
        
        Args:
            config: OpenAI configuration
        """
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Initialize OpenAI client
        client_kwargs = {"api_key": config.api_key}
        if config.organization:
            client_kwargs["organization"] = config.organization
            
        self.client = OpenAI(**client_kwargs)
        
        self.logger.info(f"OpenAI provider initialized")
        self.logger.info(f"Model: {config.model}")

    def query(self, prompt: str, **kwargs) -> str:
        """
        Send query to OpenAI
        
        Args:
            prompt: Prompt to send
            **kwargs: Additional parameters
            
        Returns:
            AI response
            
        Raises:
            AIProviderError: If query fails
        """
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # System message if provided
        if "system_message" in kwargs:
            messages.insert(0, {"role": "system", "content": kwargs["system_message"]})
        
        # Prepare parameters
        params = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            params["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            params["presence_penalty"] = kwargs["presence_penalty"]
        
        retry_settings = self.get_retry_settings()
        max_retries = retry_settings["max_retries"]
        retry_delay = retry_settings["retry_delay"]
        backoff_factor = retry_settings["backoff_factor"]
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"OpenAI query attempt {attempt + 1}/{max_retries}")
                
                response = self.client.chat.completions.create(**params)
                
                if response.choices and len(response.choices) > 0:
                    ai_response = response.choices[0].message.content
                    
                    if not self.validate_response(ai_response):
                        raise AIResponseError("Empty or invalid response from OpenAI")
                    
                    self.logger.debug(f"OpenAI response: {ai_response[:100]}...")
                    return ai_response
                else:
                    raise AIResponseError("No choices in OpenAI response")
                
            except openai.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise AIRateLimitError(f"OpenAI rate limit exceeded: {str(e)}") from e
                
                self.logger.warning(f"Rate limit hit, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
                
            except openai.APIConnectionError as e:
                if attempt == max_retries - 1:
                    raise AIConnectionError(f"OpenAI connection error: {str(e)}") from e
                
                self.logger.warning(f"Connection error, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
                
            except openai.AuthenticationError as e:
                raise AIProviderError(f"OpenAI authentication failed: {str(e)}") from e
                
            except openai.BadRequestError as e:
                raise AIProviderError(f"OpenAI bad request: {str(e)}") from e
                
            except openai.APITimeoutError as e:
                if attempt == max_retries - 1:
                    raise AIProviderError(f"OpenAI request timeout: {str(e)}") from e
                
                self.logger.warning(f"Request timeout, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
                
            except Exception as e:
                if attempt == max_retries - 1:
                    self.handle_error(e, "OpenAI query failed")
                
                self.logger.warning(f"Query failed: {str(e)}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
        
        raise AIProviderError(f"All {max_retries} attempts failed")

    def test_connection(self) -> bool:
        """
        Test connection to OpenAI
        
        Returns:
            True if connection successful
        """
        try:
            # Simple test with minimal tokens
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                temperature=0
            )
            
            if response.choices and len(response.choices) > 0:
                self.logger.info("✅ OpenAI connection successful")
                return True
            else:
                self.logger.error("❌ OpenAI connection failed: No response")
                return False
                
        except openai.AuthenticationError:
            self.logger.error("❌ OpenAI authentication failed: Invalid API key")
            return False
        except openai.APIConnectionError:
            self.logger.error("❌ OpenAI connection failed: Network error")
            return False
        except openai.RateLimitError:
            self.logger.warning("⚠️ OpenAI rate limit hit during connection test")
            return True  # Connection works, just rate limited
        except Exception as e:
            self.logger.error(f"❌ OpenAI connection test failed: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary
        """
        try:
            # Try to get model details (this may not be available for all models)
            models = self.client.models.list()
            
            for model in models.data:
                if model.id == self.config.model:
                    return {
                        "name": model.id,
                        "created": model.created,
                        "owned_by": model.owned_by,
                        "object": model.object,
                    }
            
            # If model not found in list, return basic info
            return {
                "name": self.config.model,
                "status": "configured",
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            
        except Exception as e:
            return {
                "name": self.config.model,
                "status": "error",
                "error": str(e)
            }

    def get_available_models(self) -> list[str]:
        """
        Get list of available models
        
        Returns:
            List of model names
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception:
            return []

    def prepare_prompt(self, base_prompt: str, **context) -> str:
        """
        Prepare prompt for OpenAI
        
        Args:
            base_prompt: Base prompt
            **context: Additional context
            
        Returns:
            Formatted prompt
        """
        # OpenAI handles system messages separately, so just return the prompt
        return base_prompt

    def supports_streaming(self) -> bool:
        """OpenAI supports streaming"""
        return True

    def get_retry_settings(self) -> Dict[str, Any]:
        """Get OpenAI-specific retry settings"""
        return {
            "max_retries": 5,  # Higher retries for rate limits
            "retry_delay": 1.0,
            "backoff_factor": 2.0,
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Better token estimation for OpenAI models
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # More accurate estimation for OpenAI models
        # Rough approximation: 1 token ≈ 4 characters for English text
        return max(1, len(text) // 4)

    def get_token_limit(self) -> Optional[int]:
        """
        Get context window size for the model
        
        Returns:
            Token limit for the model
        """
        # Common OpenAI model limits
        model_limits = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
        }
        
        return model_limits.get(self.config.model, self.config.max_tokens)