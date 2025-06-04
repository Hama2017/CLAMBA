import json
import re
import requests
from .config_loader import load_config
from .enums import LLMProvider

def query_llm(prompt: str, config_path: str) -> dict:
    config = load_config(config_path)
    provider = config.get("llm_provider", "openai")

    if provider == LLMProvider.OPENAI:
        return query_openai(prompt, config)
    elif provider == LLMProvider.OLLAMA:
        return query_ollama(prompt, config)
    elif provider == LLMProvider.FIREWORKS:
        return query_fireworks(prompt, config)
    else:
        raise ValueError(f"LLM provider '{provider}' non supporté.")


def query_ollama(prompt, config):
    payload = {
        "model": config["model_name"],
        "prompt": prompt,
        "temperature": config.get("temperature", 0.3),
        "max_tokens": config.get("max_tokens", 1000)
    }
    response = requests.post(config["llm_endpoint"], json=payload)
    response.raise_for_status()
    # Récupérer tout le texte brut (peut contenir plusieurs JSON concaténés)
    raw_lines = response.text.strip().splitlines()

    # Prendre seulement la dernière ligne non vide
    for line in reversed(raw_lines):
        try:
            data = json.loads(line)
            return json.loads(data.get("response", "{}"))
        except json.JSONDecodeError:
            continue

    raise ValueError("Impossible de parser la réponse JSON d'Ollama.")

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

def query_fireworks(prompt: str, config: dict) -> dict:
    url = config.get("llm_endpoint")
    model = config.get("model_name", "accounts/fireworks/models/mixtral-8x22b-instruct")
    api_key = config.get("api_key")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Tu es un assistant spécialisé en contrats juridiques."},
            {"role": "user", "content": prompt}
        ],
        "temperature": config.get("temperature", 0.5)
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    return extract_json_from_text(content)

def extract_json_from_text(text: str) -> dict:
    import json
    from json.decoder import JSONDecodeError

    start = text.find('{')
    end = text.rfind('}') + 1

    if start == -1 or end == -1:
        raise ValueError("Aucun JSON détecté dans la réponse.")

    raw_json = text[start:end]

    try:
        return json.loads(raw_json)
    except JSONDecodeError as e:
        raise ValueError(f"Erreur lors du décodage JSON : {e}")

