def classify_difficulty(prompt: str) -> str:
    prompt_lower = prompt.lower()
    
    # 1. LIVE DATA CHECK (New!)
    # If user asks for "2025", "news", or "latest", force the Live Search model
    if any(w in prompt_lower for w in ["2025", "latest", "news", "price", "today"]):
        return "HARD"
        
    # 2. Existing Checks
    complex_keywords = ["code", "debug", "architecture", "analysis"]
    if any(word in prompt_lower for word in complex_keywords):
        return "HARD"
        
    if len(prompt) < 50:
        return "SIMPLE"
    
    return "MEDIUM"