"""
Contract models for CLAMBA
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContractType(Enum):
    """Supported contract types"""
    
    LOGISTICS = "logistics"
    SALES = "sales"
    SERVICE = "service"
    REAL_ESTATE = "real_estate"
    EMPLOYMENT = "employment"
    COMMERCIAL = "commercial"
    PARTNERSHIP = "partnership"
    CONSULTING = "consulting"
    MAINTENANCE = "maintenance"
    SUPPLY = "supply"
    DISTRIBUTION = "distribution"
    FRANCHISE = "franchise"
    AUTO = "auto"  # Auto-detected


class ContractStatus(Enum):
    """Contract status"""
    
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class Position(BaseModel):
    """Position coordinates for UI elements"""
    
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class State(BaseModel):
    """Automaton state model"""
    
    id: str = Field(..., description="Unique state identifier")
    label: str = Field(..., description="Human-readable state label")
    position: Position = Field(..., description="Position in UI")
    type: str = Field(default="default", description="State type")
    source_position: str = Field(default="bottom", description="Source position for connections")
    target_position: str = Field(default="top", description="Target position for connections")
    automata_key: Optional[str] = Field(default=None, description="Automata key")
    automate_id: Optional[str] = Field(default=None, description="Automate ID")
    execution_status: Optional[str] = Field(default=None, description="Execution status")


class Transition(BaseModel):
    """Automaton transition model"""
    
    id: str = Field(..., description="Unique transition identifier")
    source: str = Field(..., description="Source state ID")
    target: str = Field(..., description="Target state ID")
    label: str = Field(..., description="Transition label")
    marker_end: str = Field(default="arrowclosed", description="Arrow marker")
    conditions: List[str] = Field(default_factory=list, description="Transition conditions")
    automata_dependencies: List[str] = Field(default_factory=list, description="Dependencies")


class ExecutionMetadata(BaseModel):
    """Execution metadata for automatons"""
    
    started_at: Optional[datetime] = Field(default=None, description="Execution start time")
    completed_at: Optional[datetime] = Field(default=None, description="Execution completion time")
    current_state: Optional[str] = Field(default=None, description="Current state ID")
    execution_log: List[Dict[str, Any]] = Field(default_factory=list, description="Execution log")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class Automate(BaseModel):
    """Automaton model"""
    
    id: str = Field(..., description="Unique automaton identifier")
    name: str = Field(..., description="Automaton name")
    active: bool = Field(default=False, description="Whether automaton is active")
    states: List[State] = Field(default_factory=list, description="Automaton states")
    transitions: List[Transition] = Field(default_factory=list, description="Automaton transitions")
    automata_dependencies: List[str] = Field(default_factory=list, description="Dependencies on other automatons")
    execution_metadata: Optional[ExecutionMetadata] = Field(default=None, description="Execution metadata")
    
    @classmethod
    def from_process(
        cls, 
        process, # Type: "Process" 
        dependencies: List[str], 
        sanitizer # Type: "IDSanitizer"
    ) -> "Automate":
        """
        Create automaton from process
        
        Args:
            process: Process to convert
            dependencies: List of dependency IDs
            sanitizer: ID sanitizer
            
        Returns:
            Automate instance
        """
        # Import here to avoid circular imports
        from ..utils.sanitizer import create_states_from_steps, create_transitions_from_steps
        
        # Create states and transitions
        states = create_states_from_steps(process.steps, sanitizer)
        transitions = create_transitions_from_steps(process.steps, dependencies, sanitizer)
        
        return cls(
            id=sanitizer.sanitize(process.id),
            name=process.name,
            active=False,
            states=states,
            transitions=transitions,
            automata_dependencies=[sanitizer.sanitize(dep) for dep in dependencies],
            execution_metadata=None
        )
    
    def get_initial_state(self) -> Optional[State]:
        """Get the initial state"""
        for state in self.states:
            if state.id == "state-initial":
                return state
        return None
    
    def get_final_states(self) -> List[State]:
        """Get final states"""
        final_states = []
        for state in self.states:
            if "completed" in state.id or "final" in state.id:
                final_states.append(state)
        return final_states
    
    def validate_structure(self) -> List[str]:
        """
        Validate automaton structure
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check if we have states
        if not self.states:
            errors.append("Automaton must have at least one state")
        
        # Check if we have initial state
        if not self.get_initial_state():
            errors.append("Automaton must have an initial state")
        
        # Check transitions reference valid states
        state_ids = {state.id for state in self.states}
        for transition in self.transitions:
            if transition.source not in state_ids:
                errors.append(f"Transition {transition.id} references unknown source state: {transition.source}")
            if transition.target not in state_ids:
                errors.append(f"Transition {transition.id} references unknown target state: {transition.target}")
        
        return errors


class Contract(BaseModel):
    """Contract model"""
    
    id: str = Field(..., description="Unique contract identifier")
    name: str = Field(..., description="Contract name")
    status: ContractStatus = Field(default=ContractStatus.DRAFT, description="Contract status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    created_by: str = Field(..., description="Creator identifier")
    description: Optional[str] = Field(default=None, description="Contract description")
    automates: List[Automate] = Field(default_factory=list, description="Contract automatons")
    contract_type: Optional[ContractType] = Field(default=None, description="Contract type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_automate_by_id(self, automate_id: str) -> Optional[Automate]:
        """Get automaton by ID"""
        for automate in self.automates:
            if automate.id == automate_id:
                return automate
        return None
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get dependency graph for all automatons
        
        Returns:
            Dictionary mapping automate IDs to their dependencies
        """
        return {
            automate.id: automate.automata_dependencies
            for automate in self.automates
        }
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate automaton dependencies
        
        Returns:
            List of validation errors
        """
        errors = []
        automate_ids = {automate.id for automate in self.automates}
        
        for automate in self.automates:
            for dep_id in automate.automata_dependencies:
                if dep_id not in automate_ids:
                    errors.append(
                        f"Automate {automate.id} depends on unknown automate: {dep_id}"
                    )
        
        return errors
    
    def has_cycles(self) -> bool:
        """
        Check if dependency graph has cycles
        
        Returns:
            True if cycles detected
        """
        from ..utils.graph import has_cycles
        
        dependency_graph = self.get_dependency_graph()
        return has_cycles(dependency_graph)
    
    def get_execution_order(self) -> List[str]:
        """
        Get topological order for automaton execution
        
        Returns:
            List of automate IDs in execution order
        """
        from ..utils.graph import topological_sort
        
        dependency_graph = self.get_dependency_graph()
        return topological_sort(dependency_graph)


class ProcessAnalysisResult(BaseModel):
    """Result of process analysis"""
    
    processes: List["Process"] = Field(..., description="Detected processes")
    detection_method: str = Field(..., description="Detection method used")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    analysis_time_seconds: float = Field(..., description="Analysis time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ContractResult(BaseModel):
    """Complete contract analysis result"""
    
    contract: Contract = Field(..., description="Generated contract")
    process_analysis: ProcessAnalysisResult = Field(..., description="Process analysis result")
    dependencies: Dict[str, List[str]] = Field(..., description="Process dependencies")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "contract": self.contract.dict(),
            "process_analysis": {
                "detection_method": self.process_analysis.detection_method,
                "confidence_score": self.process_analysis.confidence_score,
                "analysis_time_seconds": self.process_analysis.analysis_time_seconds,
                "processes_count": len(self.process_analysis.processes),
            },
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        return {
            "contract_id": self.contract.id,
            "contract_name": self.contract.name,
            "automatons_count": len(self.contract.automates),
            "processes_count": len(self.process_analysis.processes),
            "dependencies_count": sum(len(deps) for deps in self.dependencies.values()),
            "confidence_score": self.process_analysis.confidence_score,
            "analysis_time": self.process_analysis.analysis_time_seconds,
            "contract_type": self.contract.contract_type.value if self.contract.contract_type else "auto",
        }


# Forward reference resolution
from .process import Process
ProcessAnalysisResult.model_rebuild()