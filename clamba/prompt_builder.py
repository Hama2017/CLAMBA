def build_prompt(contract_text):
    return f"""
Tu es un expert en droit des contrats et en smart contracts.
Génère un fichier JSON au format .slca représentant l'automate de ce contrat.

Texte du contrat :
{contract_text}

Format attendu :
{{
  "name": "Nom du contrat",
  "states": [...],
  "transitions": [...],
  "functions": [...]
}}
"""
