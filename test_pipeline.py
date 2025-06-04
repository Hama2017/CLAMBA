
import json
from clamba.llm_interface import LLMClient
from clamba.core import ClambaPipeline

def main():
    llm_client = LLMClient()
    pipeline = ClambaPipeline(llm_client)

    # Chemin du contrat de test
    pdf_file_path = "test/contract.pdf"

    # Exécution du pipeline complet
    slca_result = pipeline.process_contract(pdf_file_path)

    # Sauvegarde du résultat
    output_path = "slca_draft_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(slca_result, f, ensure_ascii=False, indent=2)
    
    print(f"SLCA draft généré avec succès dans {output_path}")

if __name__ == "__main__":
    main()
