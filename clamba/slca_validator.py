def validate_slca(slca):
    if not isinstance(slca, dict):
        raise ValueError("SLCA must be a JSON object")
    if "states" not in slca or "transitions" not in slca:
        raise ValueError("Missing required fields in SLCA")
