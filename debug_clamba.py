#!/usr/bin/env python3
"""
Debug CLAMBA - Voir la réponse brute de l'IA
"""

from clamba.core.pdf_extractor import PDFExtractor
from clamba.ai.factory import AIProviderFactory
from clamba.config.settings import CLAMBAConfig
from pathlib import Path

def debug_ai_response():
    """Déboguer la réponse de l'IA"""
    
    print("🔍 DEBUG CLAMBA - Réponse IA")
    print("=" * 50)
    
    # Charger config
    config = CLAMBAConfig.from_file("clamba_config.yaml")
    print(f"✅ Config: {config.ai.provider}")
    
    # Extraire le texte du PDF
    pdf_path = Path("tests/contrat_prestation_service_voiture.pdf")
    extractor = PDFExtractor()
    
    try:
        contract_text = extractor.extract_text(pdf_path)
        print(f"✅ PDF extrait: {len(contract_text)} caractères")
        print("\n📄 EXTRAIT DU CONTRAT:")
        print("-" * 30)
        print(contract_text[:500] + "..." if len(contract_text) > 500 else contract_text)
        print("-" * 30)
    except Exception as e:
        print(f"❌ Erreur extraction PDF: {e}")
        return
    
    # Initialiser l'IA
    try:
        ai_provider = AIProviderFactory.create_provider(config)
        print(f"✅ Provider IA: {ai_provider.get_provider_name()}")
    except Exception as e:
        print(f"❌ Erreur provider IA: {e}")
        return
    
    # Tester la connexion
    if not ai_provider.test_connection():
        print("❌ Connexion IA échouée")
        return
    
    print("✅ Connexion IA OK")
    
    # Construire le prompt manuel (simplifié)
    prompt = f"""Tu es un EXPERT SENIOR EN ANALYSE CONTRACTUELLE.

MISSION: Analyser ce contrat pour identifier les PROCESSUS MÉTIER DISTINCTS.

CONTRAT À ANALYSER:
{contract_text[:2000]}

RÈGLES:
- Minimum 3 processus, maximum 6 processus
- Chaque processus = 3-7 étapes maximum
- Processus ACTIONNABLE et MESURABLE
- Format JSON STRICT obligatoire

FORMAT JSON EXACT:
[
  {{
    "id": "01",
    "name": "Nom du processus",
    "description": "Description du processus",
    "steps": ["étape_1", "étape_2", "étape_3"],
    "responsible_party": "Qui est responsable",
    "triggers": "Quand démarre ce processus"
  }}
]

ANALYSER LE CONTRAT ET IDENTIFIER LES PROCESSUS:"""
    
    print(f"\n📝 PROMPT ENVOYÉ ({len(prompt)} caractères):")
    print("-" * 30)
    print(prompt[-500:])  # Derniers 500 chars
    print("-" * 30)
    
    # Envoyer le prompt
    try:
        print("\n🤖 Envoi à l'IA... (peut prendre 30-60s)")
        response = ai_provider.query(prompt)
        
        print(f"\n📥 RÉPONSE BRUTE IA ({len(response)} caractères):")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
        # Analyser la réponse
        if "[" in response and "]" in response:
            print("✅ JSON array détecté dans la réponse")
            
            # Essayer d'extraire le JSON
            start = response.find('[')
            end = response.rfind(']') + 1
            json_part = response[start:end]
            
            print(f"\n📦 JSON EXTRAIT:")
            print("-" * 30)
            print(json_part)
            print("-" * 30)
            
            # Essayer de parser
            try:
                import json
                data = json.loads(json_part)
                print(f"✅ JSON valide: {len(data)} processus détectés")
                for i, proc in enumerate(data, 1):
                    print(f"   {i}. {proc.get('name', 'Nom manquant')}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON invalide: {e}")
        else:
            print("❌ Aucun JSON array trouvé dans la réponse")
            print("\n💡 L'IA n'a pas respecté le format demandé")
        
    except Exception as e:
        print(f"❌ Erreur requête IA: {e}")

def test_simple_prompt():
    """Test avec un prompt ultra-simple"""
    
    print("\n" + "=" * 50)
    print("🧪 TEST PROMPT SIMPLE")
    print("=" * 50)
    
    config = CLAMBAConfig.from_file("clamba_config.yaml")
    ai_provider = AIProviderFactory.create_provider(config)
    
    simple_prompt = """Réponds uniquement avec ce JSON exact:
[
  {
    "id": "01",
    "name": "Test Process",
    "description": "Un processus de test",
    "steps": ["step1", "step2", "step3"],
    "responsible_party": "Test",
    "triggers": "Test trigger"
  }
]"""
    
    print("📝 Prompt simple envoyé...")
    try:
        response = ai_provider.query(simple_prompt)
        print(f"📥 Réponse: {response}")
        
        if "[" in response and "]" in response:
            print("✅ Format JSON détecté")
        else:
            print("❌ Format JSON non détecté")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    debug_ai_response()
    test_simple_prompt()