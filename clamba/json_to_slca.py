import json

def convert_to_slca(clauses_json):
    """
    Transforme le JSON généré par le LLM (clauses + automates) vers le format SLCA final.
    """
    slca = {
        "name": clauses_json.get("name", "Unnamed Contract"),
        "automata": [],
        "functions": [],
        "variables": []
    }

    for clause in clauses_json.get("automata", []):
        automaton = {
            "clause_id": clause.get("clause_id", ""),
            "name": clause.get("name", ""),
            "description": clause.get("description", ""),
            "states": clause.get("states", []),
            "transitions": clause.get("transitions", []),
            "functions": [],
            "variables": []
        }
        slca["automata"].append(automaton)

    return slca


if __name__ == "__main__":
    # Exemple de test
    input_path = "slca_draft_output.json"
    output_path = "final_contract.slc"

    with open(input_path, "r", encoding="utf-8") as f:
        clauses_json = json.load(f)

    slca = convert_to_slca(clauses_json)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(slca, f, ensure_ascii=False, indent=2)

    print(f"SLCA généré et sauvegardé dans {output_path}")
