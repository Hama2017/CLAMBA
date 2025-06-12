"""
ID Sanitization utilities for CLAMBA
"""

import re
import unicodedata
from typing import List

from ..models.contract import Position, State, Transition


class IDSanitizer:
    """
    Universal ID sanitizer for generating clean identifiers
    
    Transforms any text into clean IDs without accents or special characters
    """
    
    def __init__(self, max_length: int = 50):
        """
        Initialize sanitizer
        
        Args:
            max_length: Maximum length for generated IDs
        """
        self.max_length = max_length
    
    def sanitize(self, text: str) -> str:
        """
        Sanitize text to create clean ID
        
        Args:
            text: Text to sanitize
            
        Returns:
            Clean ID string
        """
        if not text:
            return "default_id"
        
        # Step 1: Normalize accents
        text = unicodedata.normalize('NFD', str(text))
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Step 2: Convert to lowercase
        text = text.lower()
        
        # Step 3: Replace spaces and special characters with hyphens
        text = re.sub(r'[^a-z0-9]+', '-', text)
        
        # Step 4: Clean multiple hyphens and trim
        text = re.sub(r'-+', '-', text)
        text = text.strip('-')
        
        # Step 5: Limit length
        if len(text) > self.max_length:
            text = text[:self.max_length].rstrip('-')
        
        # Step 6: Ensure we have something
        if not text:
            text = "sanitized-id"
        
        return text
    
    def sanitize_step_name(self, step: str) -> str:
        """
        Sanitize step name for state creation
        
        Args:
            step: Step name to sanitize
            
        Returns:
            Sanitized step name
        """
        return self.sanitize(step.replace('_', ' '))


def create_states_from_steps(steps: List[str], sanitizer: IDSanitizer) -> List[State]:
    """
    Create automaton states from process steps
    
    Args:
        steps: List of process steps
        sanitizer: ID sanitizer instance
        
    Returns:
        List of State objects
    """
    states = []
    
    # Initial state
    states.append(State(
        id="state-initial",
        label="INITIAL",
        position=Position(x=80.0, y=80.0),
        type="default",
        source_position="bottom",
        target_position="top"
    ))
    
    # States for each step
    for i, step in enumerate(steps):
        sanitized_step = sanitizer.sanitize_step_name(step)
        
        states.append(State(
            id=f"state-{sanitized_step}",
            label=step.replace('_', ' ').title(),
            position=Position(x=80.0, y=180.0 + (i * 100)),
            type="default",
            source_position="bottom",
            target_position="top"
        ))
    
    # Final state
    states.append(State(
        id="state-completed",
        label="COMPLETED",
        position=Position(x=320.0, y=180.0 + (len(steps) * 100)),
        type="default",
        source_position="bottom",
        target_position="top"
    ))
    
    return states


def create_transitions_from_steps(
    steps: List[str], 
    dependencies: List[str], 
    sanitizer: IDSanitizer
) -> List[Transition]:
    """
    Create automaton transitions from process steps
    
    Args:
        steps: List of process steps
        dependencies: List of dependency IDs
        sanitizer: ID sanitizer instance
        
    Returns:
        List of Transition objects
    """
    transitions = []
    
    if not steps:
        return transitions
    
    # Initial transition
    first_step_sanitized = sanitizer.sanitize_step_name(steps[0])
    transitions.append(Transition(
        id=f"edge-initial-to-{first_step_sanitized}",
        source="state-initial",
        target=f"state-{first_step_sanitized}",
        label=f"initial_to_{first_step_sanitized.replace('-', '_')}",
        marker_end="arrowclosed",
        conditions=[],
        automata_dependencies=[sanitizer.sanitize(dep) for dep in dependencies]
    ))
    
    # Transitions between steps
    for i in range(len(steps) - 1):
        current_step_sanitized = sanitizer.sanitize_step_name(steps[i])
        next_step_sanitized = sanitizer.sanitize_step_name(steps[i + 1])
        
        transitions.append(Transition(
            id=f"edge-{current_step_sanitized}-to-{next_step_sanitized}",
            source=f"state-{current_step_sanitized}",
            target=f"state-{next_step_sanitized}",
            label=f"{current_step_sanitized.replace('-', '_')}_to_{next_step_sanitized.replace('-', '_')}",
            marker_end="arrowclosed",
            conditions=[],
            automata_dependencies=[]
        ))
    
    # Final transition
    last_step_sanitized = sanitizer.sanitize_step_name(steps[-1])
    transitions.append(Transition(
        id=f"edge-{last_step_sanitized}-to-completed",
        source=f"state-{last_step_sanitized}",
        target="state-completed",
        label=f"{last_step_sanitized.replace('-', '_')}_to_completed",
        marker_end="arrowclosed",
        conditions=[],
        automata_dependencies=[]
    ))
    
    return transitions


def validate_id(id_string: str) -> bool:
    """
    Validate if a string is a valid ID
    
    Args:
        id_string: String to validate
        
    Returns:
        True if valid ID
    """
    if not id_string:
        return False
    
    # Check if ID only contains lowercase letters, numbers, and hyphens
    pattern = re.compile(r'^[a-z0-9-]+$')
    if not pattern.match(id_string):
        return False
    
    # Check if ID doesn't start or end with hyphen
    if id_string.startswith('-') or id_string.endswith('-'):
        return False
    
    # Check for consecutive hyphens
    if '--' in id_string:
        return False
    
    return True


def generate_unique_id(base_id: str, existing_ids: set, sanitizer: IDSanitizer) -> str:
    """
    Generate unique ID from base ID
    
    Args:
        base_id: Base ID to make unique
        existing_ids: Set of existing IDs
        sanitizer: ID sanitizer instance
        
    Returns:
        Unique ID
    """
    sanitized_base = sanitizer.sanitize(base_id)
    
    if sanitized_base not in existing_ids:
        return sanitized_base
    
    # Add counter suffix
    counter = 1
    while True:
        candidate = f"{sanitized_base}-{counter}"
        if candidate not in existing_ids:
            return candidate
        counter += 1


class IDRegistry:
    """
    Registry for tracking used IDs and ensuring uniqueness
    """
    
    def __init__(self):
        """Initialize empty registry"""
        self.used_ids: set = set()
        self.sanitizer = IDSanitizer()
    
    def register_id(self, base_id: str) -> str:
        """
        Register and return unique ID
        
        Args:
            base_id: Base ID to register
            
        Returns:
            Unique registered ID
        """
        unique_id = generate_unique_id(base_id, self.used_ids, self.sanitizer)
        self.used_ids.add(unique_id)
        return unique_id
    
    def is_available(self, id_string: str) -> bool:
        """
        Check if ID is available
        
        Args:
            id_string: ID to check
            
        Returns:
            True if available
        """
        return id_string not in self.used_ids
    
    def reserve_id(self, id_string: str) -> bool:
        """
        Reserve an ID if available
        
        Args:
            id_string: ID to reserve
            
        Returns:
            True if successfully reserved
        """
        if self.is_available(id_string):
            self.used_ids.add(id_string)
            return True
        return False
    
    def get_stats(self) -> dict:
        """Get registry statistics"""
        return {
            "total_ids": len(self.used_ids),
            "sample_ids": list(self.used_ids)[:10] if self.used_ids else []
        }