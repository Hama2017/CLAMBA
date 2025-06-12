#!/usr/bin/env python3
"""
Convertisseur CLAMBA → SLCA Simplifié
Génère un format SLCA épuré avec dépendances intégrées dans les transitions
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class CLAMBAtoSLCASimpleConverter:
    """Convertit les fichiers CLAMBA vers le format SLCA simplifié"""
    
    def __init__(self):
        self.converter_version = "1.0.0"
    
    def convert_contract(self, clamba_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convertit un contrat CLAMBA vers SLCA simplifié"""
        
        # Extraire les dépendances globales
        global_dependencies = clamba_data.get("dependencies", {})
        
        # Structure SLCA simplifiée
        slca_contract = {
            "id": clamba_data.get("id", "unknown"),
            "name": clamba_data.get("name", "Contrat sans nom"),
            "status": clamba_data.get("status", "draft"),
            "created_at": clamba_data.get("created_at", datetime.now().isoformat()),
            "updated_at": clamba_data.get("updated_at", datetime.now().isoformat()),
            "created_by": clamba_data.get("created_by", "clamba-ai"),
            "description": clamba_data.get("description", "Contract converted to SLCA"),
            "automates": self._convert_automates(clamba_data.get("automates", []), global_dependencies)
        }
        
        return slca_contract
    
    def _convert_automates(self, automates: List[Dict[str, Any]], global_dependencies: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Convertit les automates avec dépendances intégrées"""
        converted_automates = []
        
        for automate in automates:
            automate_id = automate.get("id", "unknown")
            
            # Extraire les dépendances pour cet automate
            dependencies = []
            
            # Dépendances depuis l'automate lui-même
            automate_deps = automate.get("automata_dependencies", [])
            if automate_deps:
                dependencies.extend(automate_deps)
            
            # Dépendances depuis les dépendances globales
            global_deps = global_dependencies.get(automate_id, [])
            if global_deps:
                dependencies.extend(global_deps)
            
            # Supprimer les doublons
            dependencies = list(set(dependencies))
            
            converted_automate = {
                "id": automate.get("id", "unknown"),
                "name": automate.get("name", "Processus sans nom"),
                "active": automate.get("active", False),
                "states": self._convert_states(automate.get("states", [])),
                "transitions": self._convert_transitions(automate.get("transitions", []), dependencies),
                "execution_metadata": automate.get("execution_metadata")
            }
            
            # Supprimer les champs null/vides pour un JSON plus propre
            if converted_automate["execution_metadata"] is None:
                del converted_automate["execution_metadata"]
            
            converted_automates.append(converted_automate)
        
        return converted_automates
    
    def _convert_states(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convertit les états en supprimant les champs inutiles"""
        converted_states = []
        
        for state in states:
            converted_state = {
                "id": state.get("id", "unknown"),
                "label": state.get("label", "État sans nom"),
                "position": state.get("position", {"x": 80.0, "y": 80.0}),
                "type": state.get("type", "default")
            }
            
            # Ajouter les positions source/target si elles existent (pour compatibilité)
            if "source_position" in state:
                converted_state["source_position"] = state["source_position"]
            if "target_position" in state:
                converted_state["target_position"] = state["target_position"]
            if "sourcePosition" in state:
                converted_state["sourcePosition"] = state["sourcePosition"]
            if "targetPosition" in state:
                converted_state["targetPosition"] = state["targetPosition"]
            
            converted_states.append(converted_state)
        
        return converted_states
    
    def _convert_transitions(self, transitions: List[Dict[str, Any]], automate_dependencies: List[str]) -> List[Dict[str, Any]]:
        """Convertit les transitions en intégrant les dépendances sur la première"""
        converted_transitions = []
        
        for i, transition in enumerate(transitions):
            converted_transition = {
                "id": transition.get("id", "unknown"),
                "source": transition.get("source", "unknown"),
                "target": transition.get("target", "unknown"),
                "label": transition.get("label", "transition"),
            }
            
            # Ajouter marker_end ou markerEnd selon le format d'origine
            if "marker_end" in transition:
                converted_transition["marker_end"] = transition["marker_end"]
            elif "markerEnd" in transition:
                converted_transition["markerEnd"] = transition["markerEnd"]
            else:
                converted_transition["marker_end"] = "arrowclosed"
            
            # Garder les conditions existantes
            converted_transition["conditions"] = transition.get("conditions", [])
            
            # IMPORTANT: Intégrer les dépendances sur la PREMIÈRE transition
            if i == 0 and automate_dependencies:
                # Utiliser le bon nom de champ selon le format d'origine
                if any("automata_dependencies" in t for t in transitions):
                    converted_transition["automata_dependencies"] = automate_dependencies
                elif any("automataDependencies" in t for t in transitions):
                    converted_transition["automataDependencies"] = automate_dependencies
                else:
                    converted_transition["automata_dependencies"] = automate_dependencies
            else:
                # Autres transitions : pas de dépendances ou garder celles existantes
                if "automata_dependencies" in transition:
                    dep_value = transition["automata_dependencies"]
                    if dep_value:  # Seulement si non vide
                        converted_transition["automata_dependencies"] = dep_value
                elif "automataDependencies" in transition:
                    dep_value = transition["automataDependencies"]
                    if dep_value:  # Seulement si non vide
                        converted_transition["automataDependencies"] = dep_value
            
            converted_transitions.append(converted_transition)
        
        return converted_transitions
    
    def convert_file(self, input_file: Path, output_file: Optional[Path] = None) -> Path:
        """Convertit un fichier CLAMBA vers SLCA simplifié"""
        
        # Lire le fichier CLAMBA
        with open(input_file, 'r', encoding='utf-8') as f:
            clamba_data = json.load(f)
        
        # Convertir vers SLCA simplifié
        slca_data = self.convert_contract(clamba_data)
        
        # Déterminer le fichier de sortie
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_slca.json"
        
        # Sauvegarder le fichier SLCA
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(slca_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def print_summary(self, input_file: Path, output_file: Path):
        """Affiche un résumé de la conversion"""
        
        # Lire les fichiers pour les statistiques
        with open(input_file, 'r', encoding='utf-8') as f:
            clamba_data = json.load(f)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            slca_data = json.load(f)
        
        print(f"✅ Conversion CLAMBA → SLCA réussie")
        print(f"📁 Fichier d'entrée: {input_file}")
        print(f"📁 Fichier de sortie: {output_file}")
        print(f"📊 Automates: {len(slca_data.get('automates', []))}")
        
        # Compter les dépendances intégrées
        total_deps = 0
        for automate in slca_data.get('automates', []):
            for transition in automate.get('transitions', []):
                deps = transition.get('automata_dependencies', transition.get('automataDependencies', []))
                if deps:
                    total_deps += len(deps)
                    break  # Seulement la première transition compte
        
        print(f"📊 Dépendances intégrées: {total_deps}")
        
        # Taille des fichiers
        import os
        original_size = os.path.getsize(input_file)
        slca_size = os.path.getsize(output_file)
        reduction = ((original_size - slca_size) / original_size) * 100
        
        print(f"📏 Taille originale: {original_size:,} bytes")
        print(f"📏 Taille SLCA: {slca_size:,} bytes")
        print(f"📏 Réduction: {reduction:.1f}%")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Convertisseur CLAMBA vers SLCA Simplifié")
    parser.add_argument("input_file", help="Fichier CLAMBA JSON à convertir")
    parser.add_argument("-o", "--output", help="Fichier SLCA de sortie")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux avec statistiques")
    parser.add_argument("-q", "--quiet", action="store_true", help="Mode silencieux")
    
    args = parser.parse_args()
    
    # Vérifier que le fichier d'entrée existe
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"❌ Erreur: Le fichier {input_file} n'existe pas")
        return 1
    
    # Convertir
    converter = CLAMBAtoSLCASimpleConverter()
    
    try:
        output_file = converter.convert_file(
            input_file, 
            Path(args.output) if args.output else None
        )
        
        if not args.quiet:
            if args.verbose:
                converter.print_summary(input_file, output_file)
            else:
                print(f"✅ Fichier SLCA généré: {output_file}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())