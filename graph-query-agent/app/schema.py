# apps/graph-query-agent/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class EntityRequest(BaseModel):
    name: str

class EntityNode(BaseModel):
    name: str
    type: Optional[str] = None
    file: Optional[str] = None

class CypherRequest(BaseModel):
    query: str

class CypherResponse(BaseModel):
    results: List[dict]
