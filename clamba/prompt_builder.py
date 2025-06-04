def build_extraction_prompt(contract_text):
    return f"""
Tu es un expert juridique spécialisé en droit des contrats et en modélisation de processus.

Analyse le contrat suivant et extrait chaque clause sous forme structurée.

Pour chaque clause, génère un objet JSON avec les champs suivants :
- clause_id : identifiant unique (C1, C2, ...)
- title : un titre court de la clause
- content : le texte complet de la clause
- possible_states : une liste des états logiques qui peuvent représenter le cycle de vie de cette clause

Voici le contrat :

{contract_text}

Retourne uniquement la liste des clauses sous forme de tableau JSON, sans aucun commentaire supplémentaire.
"""


def build_slca_generation_prompt(extracted_clauses_json):
    return f"""
Tu es un expert en smart contracts et en modélisation d'automates multi-échelles.

Tu reçois ci-dessous des clauses juridiques extraites d'un contrat. Ta mission est de générer un fichier SLCA draft à partir de ces clauses.

Structure de sortie attendue :
{{
  "name": "Nom du contrat",
  "automata": [
    {{
      "clause_id": "C1",
      "name": "Titre de la clause",
      "description": "Contenu de la clause",
      "states": [liste des états pour cette clause],
      "transitions": [
        {{
          "from": "Initial",
          "to": "Running"
        }},
        {{
          "from": "Running",
          "to": "Done",
          "condition": {{
            "type": "clause_dependency",
            "dependencies": ["C2", "C5"]
          }}
        }}
      ]
    }}
  ]
}}

Les dépendances doivent représenter les clauses dont l'exécution de cette clause dépend. Si aucune dépendance : liste vide []

Voici les clauses à transformer :

{extracted_clauses_json}

Retourne uniquement le JSON sans aucun commentaire.
"""
