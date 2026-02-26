from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    natural_language_answer: str
    sql_query: str
    token_usage: TokenUsage
    latency_ms: int
    provider: str
    model: str
    status: str
