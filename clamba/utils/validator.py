"""
Validation utilities for CLAMBA
"""

from typing import List

from ..models.contract import Contract


class ResultValidator:
    """Validator for contract analysis results"""
    
    def validate_contract(self, contract: Contract) -> List[str]:
        """
        Validate contract structure
        
        Args:
            contract: Contract to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic contract validation
        if not contract.id:
            errors.append("Contract must have an ID")
        
        if not contract.name:
            errors.append("Contract must have a name")
        
        if not contract.automates:
            errors.append("Contract must have at least one automate")
        
        # Validate automates
        for automate in contract.automates:
            automate_errors = automate.validate_structure()
            errors.extend([f"Automate {automate.id}: {error}" for error in automate_errors])
        
        # Validate dependencies
        dependency_errors = contract.validate_dependencies()
        errors.extend(dependency_errors)
        
        # Check for cycles
        if contract.has_cycles():
            errors.append("Contract dependency graph has cycles")
        
        return errors