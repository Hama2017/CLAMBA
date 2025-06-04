import json
from clamba import prompt_builder
from clamba import pdf_extractor
from clamba.safe_json import safe_json_loads

class ClambaPipeline:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def extract_clauses(self, contract_text):
        extraction_prompt = prompt_builder.build_extraction_prompt(contract_text)
        extraction_response = self.llm_client.ask(extraction_prompt)
        extracted_clauses = safe_json_loads(extraction_response)
        return extracted_clauses

    def generate_slca(self, extracted_clauses):
        clauses_json = json.dumps(extracted_clauses, ensure_ascii=False, indent=2)
        slca_prompt = prompt_builder.build_slca_generation_prompt(clauses_json)
        slca_response = self.llm_client.ask(slca_prompt)
        slca_data = safe_json_loads(slca_response)
        return slca_data

    def process_contract(self, pdf_path):
        contract_text = pdf_extractor.extract_text_from_pdf(pdf_path)
        print("\n=== Extraction du texte terminé ===\n")

        extracted_clauses = self.extract_clauses(contract_text)
        print("\n=== Extraction des clauses terminé ===\n")

        slca_draft = self.generate_slca(extracted_clauses)
        print("\n=== Génération du SLCA draft terminé ===\n")

        return slca_draft

# Exemple d'utilisation
if __name__ == "__main__":
    from clamba.llm_interface import LLMClient
    
    llm_client = LLMClient()
    pipeline = ClambaPipeline(llm_client)
    
    pdf_file_path = "test/contract.pdf"
    
    slca_result = pipeline.process_contract(pdf_file_path)

    with open("slca_draft_output.json", "w", encoding="utf-8") as f:
        json.dump(slca_result, f, ensure_ascii=False, indent=2)
    
    print("SLCA draft généré avec succès dans slca_draft_output.json")
