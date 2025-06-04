def validate_slca(slca):
    if not isinstance(slca, dict):
        raise ValueError("SLCA must be a JSON object")
    
    if "automates" not in slca:
        raise ValueError("Missing 'automates' field in SLCA")
    
    if not isinstance(slca["automates"], list):
        raise ValueError("'automates' must be a list")
    
    if len(slca["automates"]) == 0:
        raise ValueError("SLCA must contain at least one automate")
    
    # Valider chaque automate
    for i, automate in enumerate(slca["automates"]):
        if not isinstance(automate, dict):
            raise ValueError(f"Automate {i} must be an object")
        
        if "states" not in automate:
            raise ValueError(f"Automate {i} missing 'states' field")
        
        if "transitions" not in automate:
            raise ValueError(f"Automate {i} missing 'transitions' field")
        
        if "id" not in automate:
            raise ValueError(f"Automate {i} missing 'id' field")
        
        if "name" not in automate:
            raise ValueError(f"Automate {i} missing 'name' field")
    
    print("✅ SLCA validation passed!")
    return True