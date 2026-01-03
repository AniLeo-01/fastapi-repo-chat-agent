from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class QueryAnalysis(BaseModel):
    query: str
    intent: str
    agents: List[str]

class SynthesisResult(BaseModel):
    session_id: str
    response: Any
