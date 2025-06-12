"""
Process models for CLAMBA
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ProcessType(Enum):
    """Business process types"""
    
    RECEPTION = "reception"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    PAYMENT = "payment"
    DELIVERY = "delivery"
    MAINTENANCE = "maintenance"
    DOCUMENTATION = "documentation"
    QUALIFICATION = "qualification"
    APPROVAL = "approval"
    STORAGE = "storage"
    TRANSPORT = "transport"
    CUSTOMS = "customs"
    BILLING = "billing"
    WARRANTY = "warranty"
    SUPPORT = "support"
    OTHER = "other"


class ProcessPriority(Enum):
    """Process priority levels"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProcessStep(BaseModel):
    """Individual step within a process"""
    
    id: str = Field(..., description="Step identifier")
    name: str = Field(..., description="Step name")
    description: Optional[str] = Field(default=None, description="Step description")
    order: int = Field(..., description="Step order in process")
    estimated_duration: Optional[str] = Field(default=None, description="Estimated duration")
    responsible_party: Optional[str] = Field(default=None, description="Who is responsible")
    conditions: List[str] = Field(default_factory=list, description="Conditions to execute step")
    outputs: List[str] = Field(default_factory=list, description="Step outputs")
    
    @validator("order")
    def validate_order(cls, v):
        if v < 0:
            raise ValueError("Order must be non-negative")
        return v


class Process(BaseModel):
    """Business process model"""
    
    id: str = Field(..., description="Unique process identifier")
    name: str = Field(..., description="Process name")
    description: Optional[str] = Field(default=None, description="Process description")
    process_type: ProcessType = Field(default=ProcessType.OTHER, description="Process type")
    priority: ProcessPriority = Field(default=ProcessPriority.MEDIUM, description="Process priority")
    steps: List[str] = Field(..., description="Process steps as strings")  # Keep compatibility
    detailed_steps: List[ProcessStep] = Field(default_factory=list, description="Detailed step objects")
    responsible_party: Optional[str] = Field(default=None, description="Who is responsible for process")
    triggers: Optional[str] = Field(default=None, description="What triggers this process")
    estimated_duration: Optional[str] = Field(default=None, description="Estimated total duration")
    prerequisites: List[str] = Field(default_factory=list, description="Process prerequisites")
    deliverables: List[str] = Field(default_factory=list, description="Process deliverables")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator("steps")
    def validate_steps(cls, v):
        if not v:
            raise ValueError("Process must have at least one step")
        if len(v) > 10:  # Reasonable limit
            raise ValueError("Process cannot have more than 10 steps")
        return v
    
    @classmethod
    def from_ai_response(
        cls,
        process_data: Dict[str, Any],
        process_type: Optional[ProcessType] = None
    ) -> "Process":
        """
        Create process from AI response data
        
        Args:
            process_data: Dictionary from AI response
            process_type: Optional process type override
            
        Returns:
            Process instance
        """
        # Extract basic fields
        process_id = process_data.get("id", "unknown")
        name = process_data.get("name", "Unknown Process")
        description = process_data.get("description", "")
        steps = process_data.get("steps", [])
        responsible_party = process_data.get("responsible_party", "")
        triggers = process_data.get("triggers", "")
        
        # Create detailed steps from string steps
        detailed_steps = []
        for i, step_name in enumerate(steps):
            detailed_steps.append(ProcessStep(
                id=f"step-{i+1}",
                name=step_name,
                order=i,
                responsible_party=responsible_party
            ))
        
        # Infer process type from name/description if not provided
        if process_type is None:
            process_type = cls._infer_process_type(name, description)
        
        return cls(
            id=process_id,
            name=name,
            description=description,
            process_type=process_type,
            steps=steps,
            detailed_steps=detailed_steps,
            responsible_party=responsible_party,
            triggers=triggers
        )
    
    @staticmethod
    def _infer_process_type(name: str, description: str) -> ProcessType:
        """
        Infer process type from name and description
        
        Args:
            name: Process name
            description: Process description
            
        Returns:
            Inferred ProcessType
        """
        text = f"{name} {description}".lower()
        
        # Simple keyword-based inference
        type_keywords = {
            ProcessType.RECEPTION: ["reception", "réception", "accueil", "receive"],
            ProcessType.PREPARATION: ["preparation", "préparation", "setup", "prepare"],
            ProcessType.EXECUTION: ["execution", "exécution", "perform", "execute", "do"],
            ProcessType.VALIDATION: ["validation", "verify", "check", "approve", "confirm"],
            ProcessType.PAYMENT: ["payment", "paiement", "pay", "billing", "invoice"],
            ProcessType.DELIVERY: ["delivery", "livraison", "deliver", "ship", "send"],
            ProcessType.TRANSPORT: ["transport", "shipping", "logistics", "move"],
            ProcessType.STORAGE: ["storage", "stockage", "store", "warehouse"],
            ProcessType.CUSTOMS: ["customs", "douane", "border", "import", "export"],
            ProcessType.DOCUMENTATION: ["documentation", "document", "record", "report"],
            ProcessType.QUALIFICATION: ["qualification", "qualify", "assess", "evaluate"],
            ProcessType.MAINTENANCE: ["maintenance", "maintain", "repair", "service"],
            ProcessType.WARRANTY: ["warranty", "garantie", "guarantee", "support"],
        }
        
        for process_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return process_type
        
        return ProcessType.OTHER
    
    def get_step_by_name(self, step_name: str) -> Optional[ProcessStep]:
        """Get detailed step by name"""
        for step in self.detailed_steps:
            if step.name == step_name:
                return step
        return None
    
    def add_step(self, step_name: str, description: Optional[str] = None) -> None:
        """Add a new step to the process"""
        # Add to simple steps list
        self.steps.append(step_name)
        
        # Add to detailed steps
        step_order = len(self.detailed_steps)
        detailed_step = ProcessStep(
            id=f"step-{step_order + 1}",
            name=step_name,
            description=description,
            order=step_order,
            responsible_party=self.responsible_party
        )
        self.detailed_steps.append(detailed_step)
    
    def remove_step(self, step_name: str) -> bool:
        """Remove a step from the process"""
        if step_name in self.steps:
            self.steps.remove(step_name)
            
            # Remove from detailed steps and reorder
            self.detailed_steps = [
                step for step in self.detailed_steps 
                if step.name != step_name
            ]
            
            # Reorder remaining steps
            for i, step in enumerate(self.detailed_steps):
                step.order = i
                step.id = f"step-{i + 1}"
            
            return True
        return False
    
    def get_duration_estimate(self) -> Optional[str]:
        """Get total duration estimate"""
        if self.estimated_duration:
            return self.estimated_duration
        
        # Try to calculate from detailed steps
        if self.detailed_steps:
            step_durations = [
                step.estimated_duration for step in self.detailed_steps 
                if step.estimated_duration
            ]
            if step_durations:
                return f"Sum of steps: {', '.join(step_durations)}"
        
        return None
    
    def get_complexity_score(self) -> float:
        """
        Calculate process complexity score (0-1)
        
        Returns:
            Complexity score based on various factors
        """
        score = 0.0
        
        # Base score from number of steps
        score += min(len(self.steps) / 10.0, 0.4)  # Max 0.4 for steps
        
        # Add score for detailed information
        if self.detailed_steps:
            score += 0.1
        
        if self.prerequisites:
            score += min(len(self.prerequisites) / 5.0, 0.2)  # Max 0.2
        
        if self.risks:
            score += min(len(self.risks) / 3.0, 0.2)  # Max 0.2
        
        # Priority factor
        priority_weights = {
            ProcessPriority.LOW: 0.0,
            ProcessPriority.MEDIUM: 0.05,
            ProcessPriority.HIGH: 0.1,
            ProcessPriority.CRITICAL: 0.15
        }
        score += priority_weights.get(self.priority, 0.0)
        
        return min(score, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.process_type.value,
            "priority": self.priority.value,
            "steps": self.steps,
            "responsible_party": self.responsible_party,
            "triggers": self.triggers,
            "estimated_duration": self.estimated_duration,
            "complexity_score": self.get_complexity_score(),
            "step_count": len(self.steps),
            "has_detailed_steps": len(self.detailed_steps) > 0,
        }


class ProcessAnalysisResult(BaseModel):
    """Result of process analysis"""
    
    processes: List[Process] = Field(..., description="Detected processes")
    detection_method: str = Field(..., description="Detection method used")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    analysis_time_seconds: float = Field(..., description="Analysis time in seconds")
    contract_type_detected: Optional[str] = Field(default=None, description="Detected contract type")
    total_steps: int = Field(..., description="Total number of steps across all processes")
    avg_complexity: float = Field(..., description="Average complexity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator("confidence_score")
    def validate_confidence_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0 and 1")
        return v
    
    def __init__(self, **data):
        # Auto-calculate fields if not provided
        if "total_steps" not in data and "processes" in data:
            data["total_steps"] = sum(len(p.steps) for p in data["processes"])
        
        if "avg_complexity" not in data and "processes" in data:
            if data["processes"]:
                complexities = [p.get_complexity_score() for p in data["processes"]]
                data["avg_complexity"] = sum(complexities) / len(complexities)
            else:
                data["avg_complexity"] = 0.0
        
        super().__init__(**data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        return {
            "process_count": len(self.processes),
            "total_steps": self.total_steps,
            "average_steps_per_process": self.total_steps / len(self.processes) if self.processes else 0,
            "confidence_score": self.confidence_score,
            "average_complexity": self.avg_complexity,
            "analysis_time": self.analysis_time_seconds,
            "detection_method": self.detection_method,
            "contract_type": self.contract_type_detected,
        }
    
    def get_processes_by_type(self) -> Dict[ProcessType, List[Process]]:
        """Group processes by type"""
        grouped = {}
        for process in self.processes:
            process_type = process.process_type
            if process_type not in grouped:
                grouped[process_type] = []
            grouped[process_type].append(process)
        return grouped
    
    def get_high_complexity_processes(self, threshold: float = 0.7) -> List[Process]:
        """Get processes with complexity above threshold"""
        return [
            process for process in self.processes 
            if process.get_complexity_score() >= threshold
        ]