from .pdf_extractor import extract_text_from_pdf
from .prompt_builder import build_prompt
from .llm_interface import query_llm
from .slca_validator import validate_slca

def generate_slca_from_pdf(pdf_path: str, config_path: str = "clamba.config.json") -> dict:
    text = extract_text_from_pdf(pdf_path)
    prompt = build_prompt(text)
    slca = query_llm(prompt, config_path)
    print("🧪 SLCA généré par le LLM :", slca)  # <--- Ajout temporaire
    validate_slca(slca)
    return slca

