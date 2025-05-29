import json
import requests
from .config_loader import load_config
from .enums import LLMProvider

def query_llm(prompt, config_path):
    config = load_config(config_path)
    provider = LLMProvider(config["llm_provider"])

    if provider == LLMProvider.OLLAMA:
        return query_ollama(prompt, config)
    elif provider == LLMProvider.OPENAI:
        return query_openai(prompt, config)
    elif provider == LLMProvider.CLAUDE:
        return query_claude(prompt, config)
    elif provider == LLMProvider.HUGGINGFACE:
        return query_huggingface(prompt, config)
    else:
        raise ValueError(f"Fournisseur LLM non supporté : {provider}")

def query_ollama(prompt, config):
    payload = {
        "model": config["model_name"],
        "prompt": prompt,
        "temperature": config.get("temperature", 0.3),
        "max_tokens": config.get("max_tokens", 1000)
    }
    response = requests.post(config["llm_endpoint"], json=payload)
    response.raise_for_status()
    return json.loads(response.json().get("response", "{}"))

def query_openai(prompt, config):
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config["model_name"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": config.get("temperature", 0.3),
        "max_tokens": config.get("max_tokens", 1000)
    }
    response = requests.post(config["llm_endpoint"], headers=headers, json=payload)
    response.raise_for_status()
    return json.loads(response.json()["choices"][0]["message"]["content"])

def query_claude(prompt, config):
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": config["model_name"],
        "max_tokens": config.get("max_tokens", 1000),
        "temperature": config.get("temperature", 0.3),
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(config["llm_endpoint"], headers=headers, json=payload)
    response.raise_for_status()
    return json.loads(response.json()["content"][0]["text"])

def query_huggingface(prompt, config):
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": config.get("temperature", 0.3),
            "max_new_tokens": config.get("max_tokens", 1000)
        }
    }
    response = requests.post(config["llm_endpoint"], headers=headers, json=payload)
    response.raise_for_status()
    return json.loads(response.json()[0]["generated_text"])
