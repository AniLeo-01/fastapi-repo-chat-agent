def should_use_cached_response(confidence: float) -> bool:
    """
    Decide whether to reuse cached agent response.
    """
    return confidence > 0.9
