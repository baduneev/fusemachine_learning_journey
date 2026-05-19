# schemas.py

from pydantic import BaseModel
from typing import Any, Optional


class AgentRequest(BaseModel):
    question: str


class AgentResponse(BaseModel):
    question: str
    decomposition: Optional[dict] = None
    sql: Optional[str] = None
    result: Any = None
    summary: Optional[str] = None
    status: str
    attempts: int
    error: Optional[str] = None