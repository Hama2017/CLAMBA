#!/usr/bin/env python3
"""
Test d'installation CLAMBA - Version simplifiée
"""

def test_basic_imports():
    """Test imports de base"""
    print("🔍 Test imports de base...")
    
    try:
        # Test import package principal
        import clamba
        print("✅ Package clamba importé")
        
        # Test version
        version = clamba.get_version()
        print(f"✅ Version: {version}")
        
        # Test info
        info = clamba.get_info()
        print(f"✅ Info: {info['name']} - {info['description']}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n⚙️ Test configuration...")
    
    try:
        from clamba.config.settings import CLAMBAConfig, create_sample_config
        
        # Créer config par défaut
        config = CLAMBAConfig()
        print(f"✅ Config par défaut: provider={config.ai.provider}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return False

def test_models():
    """Test modèles de base"""
    print("\n📋 Test modèles...")
    
    try:
        from clamba.models.process import Process, ProcessType
        from clamba.models.contract import ContractType
        
        # Test création process simple
        process = Process(
            id="test",
            name="Test Process", 
            steps=["step1", "step2"]
        )
        print(f"✅ Process créé: {process.name}")
        
        # Test enum
        print(f"✅ ContractType: {ContractType.LOGISTICS.value}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur modèles: {e}")
        return False

def test_utils():
    """Test utilitaires"""
    print("\n🔧 Test utilitaires...")
    
    try:
        from clamba.utils.sanitizer import IDSanitizer
        
        # Test sanitizer
        sanitizer = IDSanitizer()
        clean_id = sanitizer.sanitize("Test with Accents éàù")
        print(f"✅ Sanitizer: '{clean_id}'")
        
        return True
    except Exception as e:
        print(f"❌ Erreur utils: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 CLAMBA - Test simplifié")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_config,
        test_models,
        test_utils,
    ]
    
    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Erreur dans {test_func.__name__}: {e}")
    
    print(f"\n🎯 Résultat: {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("🎉 Imports de base fonctionnent !")
        print("\nEssayez maintenant:")
        print("poetry run clamba config-create")
    else:
        print("⚠️ Problèmes d'installation détectés")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())