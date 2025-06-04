import json
import os
from pathlib import Path
from datetime import datetime
from clamba.core import generate_slca_from_pdf

def test_generate_slca(pdf_path="tests/contract.pdf", save_dir="output"):
    """
    Génère un SLCA et le sauvegarde
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        save_dir: Répertoire de sauvegarde (créé automatiquement)
    """
    
    # Créer le répertoire de sortie s'il n'existe pas
    output_path = Path(save_dir)
    output_path.mkdir(exist_ok=True)
    
    # Générer le SLCA
    print(f"🔄 Génération du SLCA pour : {pdf_path}")
    slca = generate_slca_from_pdf(pdf_path, config_path="clamba.config.json")
    assert isinstance(slca, dict)
    
    # Afficher le résultat
    print("✅ SLCA généré avec succès :")
    print(json.dumps(slca, indent=2, ensure_ascii=False))
    
    # Préparer le nom de fichier
    pdf_name = Path(pdf_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder avec timestamp (optionnel)
    slca_filename = f"{pdf_name}.slca"
    slca_filename_timestamped = f"{pdf_name}_{timestamp}.slca"
    
    # Sauvegarder la version principale
    slca_path = output_path / slca_filename
    with open(slca_path, 'w', encoding='utf-8') as f:
        json.dump(slca, f, indent=2, ensure_ascii=False)
    
    # Sauvegarder la version avec timestamp (backup)
    slca_backup_path = output_path / slca_filename_timestamped
    with open(slca_backup_path, 'w', encoding='utf-8') as f:
        json.dump(slca, f, indent=2, ensure_ascii=False)
    
    # Statistiques
    file_size = os.path.getsize(slca_path)
    automate_count = len(slca.get("automates", []))
    
    print(f"\n📁 Fichiers créés :")
    print(f"   • Principal : {slca_path}")
    print(f"   • Backup    : {slca_backup_path}")
    print(f"\n📊 Statistiques :")
    print(f"   • Taille     : {file_size} octets")
    print(f"   • Automates  : {automate_count}")
    print(f"   • Contrat    : {slca.get('name', 'Sans nom')}")
    
    return slca

if __name__ == "__main__":
    # Test avec le fichier par défaut
    test_generate_slca()
    
    # Ou avec un autre fichier :
    # test_generate_slca("mon_autre_contrat.pdf", "mes_slca")