
import json
import requests
from clamba import config_loader

class LLMClient:
    def __init__(self):
        config = config_loader.load_config("clamba.config.json")
        self.provider = config["llm_provider"]
        self.endpoint = config["llm_endpoint"]
        self.model = config["model_name"]
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 2000)

    def ask(self, prompt):
        if self.provider == "ollama":
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "stream": False
            }
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        else:
            raise ValueError(f"Provider {self.provider} non supporté pour l'instant.")
