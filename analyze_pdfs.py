#!/usr/bin/env python3
"""
Analyse de contrats PDF avec CLAMBA
"""

import json
from pathlib import Path
from clamba import CLAMBAAnalyzer, CLAMBAConfig
from clamba.models.contract import ContractType

def analyze_pdfs():
    """Analyser tous les PDFs du dossier"""
    
    print("🚀 CLAMBA - Analyse de contrats PDF")
    print("=" * 50)
    
    # Charger la configuration
    try:
        config = CLAMBAConfig.from_file("clamba_config.yaml")
        print(f"✅ Configuration chargée: {config.ai.provider}")
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return
    
    # Initialiser l'analyseur
    try:
        analyzer = CLAMBAAnalyzer(config)
        print("✅ Analyseur initialisé")
    except Exception as e:
        print(f"❌ Erreur analyseur: {e}")
        return
    
    # Valider la configuration
    validation = analyzer.validate_configuration()
    if not validation["ai_provider_available"]:
        print("❌ Provider IA non disponible")
        if config.ai.provider == "ollama":
            print("💡 Assurez-vous qu'Ollama fonctionne: ollama serve")
        return
    
    print("✅ Provider IA disponible")
    
    # Trouver les PDFs
    pdf_files = list(Path(".").glob("*.pdf"))
    if not pdf_files:
        print("❌ Aucun fichier PDF trouvé dans le dossier courant")
        return
    
    print(f"📄 {len(pdf_files)} PDF(s) trouvé(s):")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Créer dossier résultats
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Analyser chaque PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n🔍 Analyse {i}/{len(pdf_files)}: {pdf_file.name}")
        
        try:
            # Analyser le contrat
            result = analyzer.analyze_contract(
                pdf_path=pdf_file,
                contract_type=ContractType.AUTO,  # Auto-détection
                custom_instructions="Focalisez sur les processus métier distincts et automatisables"
            )
            
            # Sauvegarder le résultat
            output_file = results_dir / f"{pdf_file.stem}_automates.json"
            analyzer.save_result(result, output_file)
            
            # Afficher le résumé
            summary = result.get_summary()
            print("✅ Analyse terminée:")
            print(f"   📋 Contrat: {summary['contract_name']}")
            print(f"   ⚙️  Automates: {summary['automatons_count']}")
            print(f"   🔧 Processus: {summary['processes_count']}")
            print(f"   🔗 Dépendances: {summary['dependencies_count']}")
            print(f"   📊 Confiance: {summary['confidence_score']:.2f}")
            print(f"   ⏱️  Temps: {summary['analysis_time']:.1f}s")
            print(f"   💾 Sauvé: {output_file}")
            
            # Afficher les automates générés
            print(f"\n   🤖 Automates générés:")
            for automate in result.contract.automates:
                print(f"      - {automate.name} ({len(automate.states)} états, {len(automate.transitions)} transitions)")
                if automate.automata_dependencies:
                    deps = ", ".join(automate.automata_dependencies)
                    print(f"        Dépendances: {deps}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse de {pdf_file.name}: {e}")
            continue
    
    print(f"\n🎊 Analyse terminée !")
    print(f"📁 Résultats dans: {results_dir}")
    
    # Lister les fichiers générés
    result_files = list(results_dir.glob("*.json"))
    if result_files:
        print(f"\n📋 Fichiers générés:")
        for file in result_files:
            print(f"   - {file.name}")
            
        print(f"\n💡 Pour visualiser un résultat:")
        print(f"   python -m json.tool results/{result_files[0].name}")

def show_contract_result(json_file):
    """Afficher le résultat d'un contrat de façon lisible"""
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📋 CONTRAT: {data['name']}")
        print(f"🆔 ID: {data['id']}")
        print(f"📅 Créé: {data['created_at']}")
        print(f"👤 Par: {data['created_by']}")
        print(f"📝 Description: {data['description']}")
        
        print(f"\n⚙️  AUTOMATES ({len(data['automates'])}):")
        
        for automate in data['automates']:
            print(f"\n   🤖 {automate['name']}")
            print(f"      ID: {automate['id']}")
            print(f"      États: {len(automate['states'])}")
            print(f"      Transitions: {len(automate['transitions'])}")
            print(f"      Actif: {automate['active']}")
            
            if automate['automata_dependencies']:
                print(f"      Dépendances: {', '.join(automate['automata_dependencies'])}")
            
            # Afficher les états
            print(f"      États:")
            for state in automate['states']:
                print(f"         - {state['label']} (id: {state['id']})")
            
            # Afficher les premières transitions
            if automate['transitions']:
                print(f"      Transitions (première):")
                first_transition = automate['transitions'][0]
                print(f"         - {first_transition['label']}")
                print(f"           {first_transition['source']} → {first_transition['target']}")
        
    except Exception as e:
        print(f"❌ Erreur lecture {json_file}: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        if len(sys.argv) > 2:
            show_contract_result(sys.argv[2])
        else:
            print("Usage: python script.py show fichier.json")
    else:
        analyze_pdfs()