#!/usr/bin/env python3
"""
Test d'installation CLAMBA - Version complète
"""

import sys
from pathlib import Path

def test_imports():
    """Test des imports de base"""
    print("🔍 Test des imports...")
    
    try:
        import clamba
        print(f"✅ clamba importé - version {clamba.get_version()}")
    except ImportError as e:
        print(f"❌ Erreur import clamba: {e}")
        return False
    
    try:
        from clamba import CLAMBAAnalyzer, CLAMBAConfig
        print("✅ Classes principales importées")
    except ImportError as e:
        print(f"❌ Erreur import classes: {e}")
        return False
    
    try:
        from clamba.models.contract import ContractType
        print("✅ Modèles importés")
    except ImportError as e:
        print(f"❌ Erreur import modèles: {e}")
        return False
    
    return True

def test_config():
    """Test de la configuration"""
    print("\n⚙️ Test de la configuration...")
    
    try:
        from clamba import CLAMBAConfig, create_sample_config
        
        # Créer config d'exemple
        create_sample_config("test_config.yaml")
        print("✅ Configuration d'exemple créée")
        
        # Charger config
        config = CLAMBAConfig.from_file("test_config.yaml")
        print(f"✅ Configuration chargée - provider: {config.ai.provider}")
        
        # Nettoyer
        Path("test_config.yaml").unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def test_ai_providers():
    """Test des providers IA"""
    print("\n🤖 Test des providers IA...")
    
    try:
        from clamba.ai.factory import AIProviderFactory
        
        # Test providers disponibles
        available = AIProviderFactory.get_available_providers()
        print(f"✅ Providers disponibles: {', '.join(available)}")
        
        # Test création provider Ollama
        from clamba import CLAMBAConfig
        config = CLAMBAConfig()  # Config par défaut (Ollama)
        
        try:
            provider = AIProviderFactory.create_provider(config)
            print(f"✅ Provider Ollama créé: {provider.get_provider_name()}")
            
            # Test connexion (optionnel)
            if provider.test_connection():
                print("✅ Connexion Ollama réussie")
            else:
                print("⚠️ Ollama non connecté (normal si pas démarré)")
                
        except Exception as e:
            print(f"⚠️ Provider Ollama: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur providers IA: {e}")
        return False

def test_models():
    """Test des modèles"""
    print("\n📋 Test des modèles...")
    
    try:
        from clamba.models.contract import Contract, ContractType, Automate
        from clamba.models.process import Process, ProcessType
        from clamba.utils.sanitizer import IDSanitizer
        
        # Test création process
        process = Process(
            id="test-process",
            name="Test Process",
            steps=["step1", "step2", "step3"],
            process_type=ProcessType.EXECUTION
        )
        print(f"✅ Process créé: {process.name} avec {len(process.steps)} étapes")
        
        # Test sanitizer
        sanitizer = IDSanitizer()
        clean_id = sanitizer.sanitize("Test Process with Accents éàù")
        print(f"✅ ID sanitized: '{clean_id}'")
        
        # Test automate création
        automate = Automate.from_process(process, [], sanitizer)
        print(f"✅ Automate créé: {automate.id} avec {len(automate.states)} états")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur modèles: {e}")
        return False

def test_cli():
    """Test CLI"""
    print("\n💻 Test CLI...")
    
    try:
        from clamba.cli import app
        print("✅ CLI importée")
        
        # Test info command simple
        try:
            from clamba.cli import show_banner
            show_banner()
            print("✅ Fonction CLI testée")
        except Exception as e:
            print(f"⚠️ Erreur CLI function: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur CLI: {e}")
        return False

def test_pdf_extraction():
    """Test extraction PDF"""
    print("\n📄 Test extraction PDF...")
    
    try:
        from clamba.core.pdf_extractor import PDFExtractor
        
        extractor = PDFExtractor()
        print("✅ PDFExtractor créé")
        
        # Test validation sur fichier inexistant
        valid, error = extractor.validate_pdf(Path("nonexistent.pdf"))
        if not valid and "not found" in error:
            print("✅ Validation PDF fonctionne")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur extraction PDF: {e}")
        return False

def test_analyzer():
    """Test analyseur principal"""
    print("\n🔬 Test analyseur principal...")
    
    try:
        from clamba import CLAMBAAnalyzer, CLAMBAConfig
        
        # Config par défaut
        config = CLAMBAConfig()
        
        # Créer analyseur
        analyzer = CLAMBAAnalyzer(config)
        print("✅ CLAMBAAnalyzer créé")
        
        # Test validation config
        validation = analyzer.validate_configuration()
        print(f"✅ Validation config: {validation}")
        
        # Test types de contrats supportés
        types = analyzer.get_supported_contract_types()
        print(f"✅ {len(types)} types de contrats supportés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur analyseur: {e}")
        return False

def test_utilitaires():
    """Test des utilitaires"""
    print("\n🔧 Test des utilitaires...")
    
    try:
        from clamba.utils.sanitizer import IDSanitizer
        from clamba.utils.graph import has_cycles, topological_sort
        
        # Test sanitizer
        sanitizer = IDSanitizer()
        result = sanitizer.sanitize("Test éàçù avec Espaces et Caractères_Spéciaux!")
        print(f"✅ Sanitizer: '{result}'")
        
        # Test graph utilities
        graph = {"A": ["B"], "B": [], "C": ["A"]}
        has_cycle = has_cycles(graph)
        print(f"✅ Graph cycle detection: {has_cycle}")
        
        # Test topological sort
        simple_graph = {"A": [], "B": ["A"], "C": ["B"]}
        topo_order = topological_sort(simple_graph)
        print(f"✅ Topological sort: {topo_order}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur utilitaires: {e}")
        return False

def test_complete_workflow():
    """Test workflow complet (simulation)"""
    print("\n🔄 Test workflow complet...")
    
    try:
        from clamba import CLAMBAConfig, get_info
        from clamba.models.contract import ContractType
        from clamba.models.process import Process, ProcessType
        
        # Test info package
        info = get_info()
        print(f"✅ Info package: {info['name']} v{info['version']}")
        
        # Test création de processus complet
        process = Process(
            id="workflow-test",
            name="Processus de test workflow",
            description="Test de création d'un processus complet",
            steps=["initialisation", "traitement", "validation", "finalisation"],
            process_type=ProcessType.EXECUTION,
            responsible_party="Test Team",
            triggers="Test automatique"
        )
        
        print(f"✅ Processus complet créé: {process.name}")
        print(f"   - {len(process.steps)} étapes")
        print(f"   - Type: {process.process_type.value}")
        print(f"   - Complexité: {process.get_complexity_score():.2f}")
        
        # Test configuration avancée
        config = CLAMBAConfig()
        print(f"✅ Configuration: Provider {config.ai.provider}")
        print(f"   - Format sortie: {config.output.output_format}")
        print(f"   - Debug: {config.debug}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur workflow: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 CLAMBA - Test d'installation complet")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Providers IA", test_ai_providers),
        ("Modèles", test_models),
        ("CLI", test_cli),
        ("Extraction PDF", test_pdf_extraction),
        ("Analyseur", test_analyzer),
        ("Utilitaires", test_utilitaires),
        ("Workflow complet", test_complete_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            import traceback
            print(f"   Détails: {traceback.format_exc()}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    failed_tests = []
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
        else:
            failed_tests.append(test_name)
    
    print(f"\n🎯 Résultat: {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("\n🎉 Installation CLAMBA réussie !")
        print("\n📋 Prochaines étapes:")
        print("1. 📝 Créer votre configuration:")
        print("   poetry run clamba config-create")
        print("\n2. 🤖 Configurer votre provider IA:")
        print("   - Ollama: ollama serve && ollama pull nous-hermes2")
        print("   - OpenAI: export OPENAI_API_KEY=your-key")
        print("   - Anthropic: export ANTHROPIC_API_KEY=your-key")
        print("\n3. 🔍 Tester avec un PDF:")
        print("   poetry run clamba analyze contrat.pdf")
        print("\n4. 📚 Explorer les fonctionnalités:")
        print("   poetry run clamba info")
        print("   poetry run clamba config-validate")
        
    else:
        print(f"\n⚠️ {len(failed_tests)} test(s) ont échoué:")
        for test in failed_tests:
            print(f"   - {test}")
        print("\n💡 Solutions possibles:")
        print("- Vérifier l'installation: poetry install --with dev")
        print("- Vérifier les imports manquants")
        print("- Consulter les logs d'erreur ci-dessus")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)