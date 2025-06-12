"""
Ollama AI Provider for CLAMBA
"""

import time
from typing import Any, Dict

import requests

from ..config.settings import OllamaConfig
from ..utils.logger import get_logger
from .base import (
    AIConnectionError,
    AIProviderError,
    AIRateLimitError,
    AIResponseError,
    BaseAIProvider,
)


class OllamaProvider(BaseAIProvider):
    """
    Ollama AI provider for local AI models
    
    Supports local Ollama installations for privacy and offline usage
    """

    def __init__(self, config: OllamaConfig):
        """
        Initialize Ollama provider
        
        Args:
            config: Ollama configuration
        """
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Build API URLs
        self.generate_url = f"{config.url.rstrip('/')}/api/generate"
        self.tags_url = f"{config.url.rstrip('/')}/api/tags"
        
        self.logger.info(f"Ollama provider initialized: {config.url}")
        self.logger.info(f"Model: {config.model}")

    def query(self, prompt: str, **kwargs) -> str:
        """
        Send query to Ollama
        
        Args:
            prompt: Prompt to send
            **kwargs: Additional parameters
            
        Returns:
            AI response
            
        Raises:
            AIProviderError: If query fails
        """
        # Prepare payload
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
            }
        }
        
        # Add any additional options
        if "top_p" in kwargs:
            payload["options"]["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["options"]["top_k"] = kwargs["top_k"]
        
        retry_settings = self.get_retry_settings()
        max_retries = retry_settings["max_retries"]
        retry_delay = retry_settings["retry_delay"]
        backoff_factor = retry_settings["backoff_factor"]
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Ollama query attempt {attempt + 1}/{max_retries}")
                
                response = requests.post(
                    self.generate_url,
                    json=payload,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    if not self.validate_response(ai_response):
                        raise AIResponseError("Empty or invalid response from Ollama")
                    
                    self.logger.debug(f"Ollama response: {ai_response[:100]}...")
                    return ai_response
                
                elif response.status_code == 404:
                    raise AIProviderError(f"Model '{self.config.model}' not found")
                
                elif response.status_code == 429:
                    raise AIRateLimitError("Ollama rate limit exceeded")
                
                else:
                    raise AIProviderError(f"Ollama API error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError as e:
                if attempt == max_retries - 1:
                    raise AIConnectionError(
                        f"Cannot connect to Ollama at {self.config.url}. "
                        "Make sure Ollama is running: ollama serve"
                    ) from e
                
                self.logger.warning(f"Connection failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
                
            except requests.exceptions.Timeout as e:
                if attempt == max_retries - 1:
                    raise AIProviderError(f"Ollama request timeout after {self.config.timeout}s") from e
                
                self.logger.warning(f"Request timeout, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
                
            except Exception as e:
                if attempt == max_retries - 1:
                    self.handle_error(e, "Ollama query failed")
                
                self.logger.warning(f"Query failed: {str(e)}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor
        
        raise AIProviderError(f"All {max_retries} attempts failed")

    def test_connection(self) -> bool:
        """
        Test connection to Ollama
        
        Returns:
            True if connection successful
        """
        try:
            response = requests.get(self.tags_url, timeout=10)
            
            if response.status_code == 200:
                # Check if our model is available
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                if self.config.model in model_names:
                    self.logger.info(f"✅ Ollama connection successful, model '{self.config.model}' available")
                    return True
                else:
                    self.logger.warning(f"⚠️ Ollama connected but model '{self.config.model}' not found")
                    self.logger.info(f"Available models: {', '.join(model_names)}")
                    return False
            else:
                self.logger.error(f"❌ Ollama connection failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Cannot connect to Ollama at {self.config.url}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ollama connection test failed: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary
        """
        try:
            response = requests.get(self.tags_url, timeout=10)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                for model in models:
                    if model.get("name") == self.config.model:
                        return {
                            "name": model.get("name"),
                            "size": model.get("size"),
                            "modified_at": model.get("modified_at"),
                            "digest": model.get("digest"),
                            "details": model.get("details", {}),
                        }
                
                return {"name": self.config.model, "status": "not_found"}
            else:
                return {"name": self.config.model, "status": "connection_failed"}
                
        except Exception as e:
            return {"name": self.config.model, "status": "error", "error": str(e)}

    def get_available_models(self) -> list[str]:
        """
        Get list of available models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(self.tags_url, timeout=10)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model.get("name", "") for model in models]
            else:
                return []
                
        except Exception:
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
        """
        try:
            pull_url = f"{self.config.url.rstrip('/')}/api/pull"
            payload = {"name": model_name}
            
            self.logger.info(f"Pulling model: {model_name}")
            
            response = requests.post(pull_url, json=payload, timeout=300)  # 5 minutes timeout
            
            if response.status_code == 200:
                self.logger.info(f"✅ Model '{model_name}' pulled successfully")
                return True
            else:
                self.logger.error(f"❌ Failed to pull model '{model_name}': HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error pulling model '{model_name}': {str(e)}")
            return False

    def prepare_prompt(self, base_prompt: str, **context) -> str:
        """
        Prepare prompt for Ollama (no special formatting needed)
        
        Args:
            base_prompt: Base prompt
            **context: Additional context
            
        Returns:
            Formatted prompt
        """
        return base_prompt

    def supports_streaming(self) -> bool:
        """Ollama supports streaming"""
        return True

    def get_retry_settings(self) -> Dict[str, Any]:
        """Get Ollama-specific retry settings"""
        return {
            "max_retries": 3,
            "retry_delay": 2.0,
            "backoff_factor": 1.5,
        }