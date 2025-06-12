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
                
            except openai.Authentication