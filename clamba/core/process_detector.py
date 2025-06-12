"""
Process detection module for CLAMBA
"""

import json
import re
import time
from typing import Dict, List, Optional

from ..ai.base import BaseAIProvider
from ..config.settings import CLAMBAConfig
from ..models.contract import ContractType
from ..models.process import Process, ProcessAnalysisResult, ProcessType
from ..utils.logger import get_logger


class ProcessDetector:
    """
    Business process detector using AI
    """
    
    def __init__(self, ai_provider: BaseAIProvider, config: CLAMBAConfig):
        """
        Initialize process detector
        
        Args:
            ai_provider: AI provider instance
            config: CLAMBA configuration
        """
        self.ai_provider = ai_provider
        self.config = config
        self.logger = get_logger(__name__, debug=config.debug)
    
    def detect_processes(
        self,
        contract_text: str,
        contract_type: Optional[ContractType] = None,
        custom_instructions: Optional[str] = None,
    ) -> ProcessAnalysisResult:
        """
        Detect business processes in contract text
        
        Args:
            contract_text: Contract text to analyze
            contract_type: Optional contract type hint
            custom_instructions: Optional custom analysis instructions
            
        Returns:
            ProcessAnalysisResult with detected processes
        """
        start_time = time.time()
        
        # Build detection prompt
        prompt = self._build_detection_prompt(
            contract_text, contract_type, custom_instructions
        )
        
        # Query AI
        response = self.ai_provider.query(prompt)
        
        # Parse response
        processes = self._parse_processes_response(response)
        
        analysis_time = time.time() - start_time
        
        # Calculate confidence score
        confidence = self._calculate_confidence(processes, contract_text)
        
        return ProcessAnalysisResult(
            processes=processes,
            detection_method=f"ai_{self.ai_provider.get_provider_name()}",
            confidence_score=confidence,
            analysis_time_seconds=analysis_time,
            contract_type_detected=contract_type.value if contract_type else "auto",
            metadata={
                "ai_provider": self.ai_provider.get_provider_name(),
                "prompt_length": len(prompt),
                "response_length": len(response),
                "contract_length": len(contract_text),
            }
        )
    
    def analyze_dependencies(self, processes: List[Process]) -> Dict[str, List[str]]:
        """
        Analyze dependencies between processes
        
        Args:
            processes: List of detected processes
            
        Returns:
            Dictionary mapping process IDs to their dependencies
        """
        # Build dependency analysis prompt
        prompt = self._build_dependency_prompt(processes)
        
        # Query AI
        response = self.ai_provider.query(prompt)
        
        # Parse dependencies
        dependencies = self._parse_dependencies_response(response, processes)
        
        # Validate and clean cycles
        if self.config.analysis.cycle_detection:
            dependencies = self._remove_cycles(dependencies)
        
        return dependencies
    
    def _build_detection_prompt(
        self,
        contract_text: str,
        contract_type: Optional[ContractType],
        custom_instructions: Optional[str],
    ) -> str:
        """Build AI prompt for process detection"""
        
        # Contract type examples
        type_examples = {
            ContractType.LOGISTICS: """
EXEMPLES PROCESSUS LOGISTIQUE:
- Processus réception marchandises
- Processus manutention/stockage  
- Processus douanier/administrative
- Processus facturation/paiement""",
            
            ContractType.SALES: """
EXEMPLES PROCESSUS VENTE:
- Processus préparation produit
- Processus paiement échelonné
- Processus livraison/réception
- Processus garantie/SAV""",
            
            ContractType.SERVICE: """
EXEMPLES PROCESSUS PRESTATION:
- Processus qualification besoin
- Processus exécution prestation
- Processus validation livrables
- Processus facturation""",
        }
        
        # Truncate contract text if too long
        max_contract_length = 6000
        if len(contract_text) > max_contract_length:
            contract_text = contract_text[:max_contract_length] + "..."
        
        prompt = f"""Tu es un EXPERT SENIOR EN ANALYSE CONTRACTUELLE et AUTOMATISATION DE PROCESSUS.

MISSION CRITIQUE: Analyser ce contrat pour identifier les PROCESSUS MÉTIER DISTINCTS qui peuvent être automatisés séparément.

CONTRAT À ANALYSER:
{contract_text}

MÉTHODOLOGIE UNIVERSELLE:
1. LIRE intégralement le contrat
2. IDENTIFIER les processus métier DISTINCTS et INDÉPENDANTS
3. CHAQUE processus = une série d'actions liées logiquement
4. SÉPARER les processus qui peuvent s'exécuter en parallèle
5. IGNORER les clauses juridiques pures (résiliation, juridiction, etc.)

{type_examples.get(contract_type, "") if contract_type else ""}

RÈGLES UNIVERSELLES:
- Minimum {self.config.analysis.min_processes} processus, maximum {self.config.analysis.max_processes} processus
- Chaque processus = {self.config.analysis.max_steps_per_process} étapes maximum
- Processus ACTIONNABLE et MESURABLE
- Adapté au contexte spécifique du contrat
- États logiques et séquentiels

{f"INSTRUCTIONS SPÉCIFIQUES: {custom_instructions}" if custom_instructions else ""}

FORMAT JSON STRICT:
[
  {{
    "id": "01",
    "name": "Nom du processus métier",
    "description": "Description détaillée du processus",
    "steps": ["action_1", "action_2", "action_3", "action_4"],
    "responsible_party": "Qui est responsable",
    "triggers": "Quand démarre ce processus"
  }}
]

ANALYSER LE CONTRAT ET IDENTIFIER LES PROCESSUS MÉTIER DISTINCTS:"""
        
        return prompt
    
    def _build_dependency_prompt(self, processes: List[Process]) -> str:
        """Build AI prompt for dependency analysis"""
        
        processes_info = ""
        for p in processes:
            processes_info += f"PROCESSUS {p.id}: {p.name}\n"
            processes_info += f"   Description: {p.description}\n"
            processes_info += f"   Étapes: {p.steps}\n"
            processes_info += f"   Responsable: {p.responsible_party}\n"
            processes_info += f"   Déclencheur: {p.triggers}\n\n"
        
        prompt = f"""Tu es un EXPERT EN ORCHESTRATION DE PROCESSUS MÉTIER.

MISSION: Analyser les dépendances logiques entre ces processus pour créer un DAG optimal.

PROCESSUS MÉTIER IDENTIFIÉS:
{processes_info}

RÈGLES UNIVERSELLES DÉPENDANCES - AUCUN CYCLE AUTORISÉ:
1. Un processus B dépend de A SI ET SEULEMENT si B ne peut PAS démarrer sans que A soit COMPLÉTÉ
2. Analyser la logique OPÉRATIONNELLE réelle du contrat
3. ⚠️ INTERDICTION ABSOLUE DE CYCLES: Si A dépend de B, alors B ne peut JAMAIS dépendre de A
4. VÉRIFIER qu'aucun processus ne dépend de lui-même
5. MAXIMISER l'exécution PARALLÈLE quand possible
6. En cas de doute sur une dépendance, PRÉFÉRER l'indépendance

FORMAT JSON EXACT:
{{
  "01": [],
  "02": ["01"],
  "03": ["01"],
  "04": ["02", "03"]
}}

ANALYSER LES DÉPENDANCES LOGIQUES:"""
        
        return prompt
    
    def _parse_processes_response(self, response: str) -> List[Process]:
        """Parse AI response to extract processes"""
        processes = []
        
        # Find JSON array in response
        json_match = self._extract_json_array(response)
        if not json_match:
            self.logger.warning("No JSON array found in AI response")
            return processes
        
        try:
            process_data = json.loads(json_match)
            
            for item in process_data:
                if not isinstance(item, dict):
                    continue
                
                # Validate required fields
                if not all(key in item for key in ["id", "name", "steps"]):
                    self.logger.warning(f"Invalid process data: {item}")
                    continue
                
                # Create process
                process = Process.from_ai_response(item)
                processes.append(process)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse processes JSON: {e}")
        
        return processes
    
    def _parse_dependencies_response(
        self, response: str, processes: List[Process]
    ) -> Dict[str, List[str]]:
        """Parse AI response to extract dependencies"""
        
        # Find JSON object in response
        json_match = self._extract_json_object(response)
        if not json_match:
            self.logger.warning("No JSON object found in dependencies response")
            return {}
        
        try:
            deps_data = json.loads(json_match)
            
            if not isinstance(deps_data, dict):
                return {}
            
            # Validate dependencies against actual process IDs
            process_ids = {p.id for p in processes}
            valid_deps = {}
            
            for process_id in process_ids:
                if process_id in deps_data:
                    # Filter valid dependencies
                    valid_deps[process_id] = [
                        dep for dep in deps_data[process_id]
                        if dep in process_ids and dep != process_id  # No self-dependencies
                    ]
                else:
                    valid_deps[process_id] = []
            
            return valid_deps
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse dependencies JSON: {e}")
            return {}
    
    def _extract_json_array(self, text: str) -> Optional[str]:
        """Extract JSON array from text"""
        start_idx = text.find('[')
        if start_idx == -1:
            return None
        
        bracket_count = 0
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    return text[start_idx:i+1]
        
        return None
    
    def _extract_json_object(self, text: str) -> Optional[str]:
        """Extract JSON object from text"""
        start_idx = text.find('{')
        if start_idx == -1:
            return None
        
        brace_count = 0
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start_idx:i+1]
        
        return None
    
    def _calculate_confidence(self, processes: List[Process], contract_text: str) -> float:
        """Calculate confidence score for process detection"""
        
        if not processes:
            return 0.0
        
        score = 0.0
        
        # Base score from number of processes
        expected_processes = (self.config.analysis.min_processes + self.config.analysis.max_processes) / 2
        process_score = min(len(processes) / expected_processes, 1.0) * 0.3
        score += process_score
        
        # Score from process completeness
        complete_processes = sum(
            1 for p in processes 
            if p.name and p.description and p.steps and p.responsible_party
        )
        completeness_score = (complete_processes / len(processes)) * 0.3
        score += completeness_score
        
        # Score from step quality
        total_steps = sum(len(p.steps) for p in processes)
        avg_steps = total_steps / len(processes) if processes else 0
        step_score = min(avg_steps / 5.0, 1.0) * 0.2  # Optimal around 5 steps
        score += step_score
        
        # Score from process diversity
        process_types = {p.process_type for p in processes}
        diversity_score = min(len(process_types) / len(processes), 1.0) * 0.2
        score += diversity_score
        
        return min(score, 1.0)
    
    def _remove_cycles(self, dependencies: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Remove cycles from dependency graph"""
        from ..utils.graph import has_cycles, remove_cycles
        
        if not has_cycles(dependencies):
            return dependencies
        
        self.logger.warning("Cycles detected in dependencies, removing...")
        clean_deps = remove_cycles(dependencies)
        
        return clean_deps