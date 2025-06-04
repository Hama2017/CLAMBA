import json
import re

def safe_json_loads(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # tentative de nettoyage rapide : supprimer les * et caractères illégaux connus
        cleaned_text = re.sub(r"\\*", "", text)
        cleaned_text = re.sub(r",\\s*([}}\]])", r"\\1", cleaned_text)  # trailing commas
        cleaned_text = re.sub(r"\n", "", cleaned_text)  # supprimer les sauts de lignes
        cleaned_text = re.sub(r"\\s+", " ", cleaned_text)  # compacter les espaces
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            raise ValueError("Impossible de parser même après nettoyage")
