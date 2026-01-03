from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

class ConversationTurn(BaseModel):
    timestamp: datetime
    query: str
    response: Any

class AgentInvocation(BaseModel):
    agent_name: str
    input: Dict[str, Any]
    output: Dict[str, Any]

class RoutingDecision(BaseModel):
    query: str
    intent: str
    agents: List[str]

class UserContext(BaseModel):
    preferences: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
