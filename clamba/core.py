from .pdf_extractor import extract_text_from_pdf
from .prompt_builder import build_prompt
from .llm_interface import query_llm
from .slca_validator import validate_slca

def generate_slca_from_pdf(pdf_path, config_path="clamba.config.json"):
    text = extract_text_from_pdf(pdf_path)
    prompt = build_prompt(text)
    slca = query_llm(prompt, config_path)
    validate_slca(slca)
    return slca
