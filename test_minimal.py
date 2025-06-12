#!/usr/bin/env python3
"""
Test minimal CLAMBA
"""

# Test 1: Import du package
print("Test 1: Import package...")
try:
    import clamba
    print("✅ Package importé")
except Exception as e:
    print(f"❌ Erreur import: {e}")
    exit(1)

# Test 2: get_version
print("\nTest 2: get_version...")
try:
    version = clamba.get_version()
    print(f"✅ Version: {version}")
except Exception as e:
    print(f"❌ Erreur get_version: {e}")

# Test 3: get_info
print("\nTest 3: get_info...")
try:
    info = clamba.get_info()
    print(f"✅ Info: {info}")
except Exception as e:
    print(f"❌ Erreur get_info: {e}")

# Test 4: IDSanitizer direct
print("\nTest 4: IDSanitizer...")
try:
    from clamba.utils.sanitizer import IDSanitizer
    sanitizer = IDSanitizer()
    result = sanitizer.sanitize("Test éàù")
    print(f"✅ IDSanitizer: '{result}'")
except Exception as e:
    print(f"❌ Erreur IDSanitizer: {e}")

# Test 5: Configuration
print("\nTest 5: Configuration...")
try:
    from clamba.config.settings import CLAMBAConfig
    config = CLAMBAConfig()
    print(f"✅ Config: provider={config.ai.provider}")
except Exception as e:
    print(f"❌ Erreur config: {e}")

# Test 6: Models
print("\nTest 6: Models...")
try:
    from clamba.models.process import Process
    process = Process(id="test", name="Test", steps=["step1"])
    print(f"✅ Process: {process.name}")
except Exception as e:
    print(f"❌ Erreur models: {e}")

print("\n🎯 Test minimal terminé!")