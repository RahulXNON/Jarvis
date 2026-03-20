from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint (streaming)."""
    response: str


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    ollama: bool
    memory: bool
    uptime_seconds: int


class TaskItem(BaseModel):
    """Model for individual task items."""
    session_id: str
    message: str
    response_preview: str
    response_time_ms: int
    timestamp: str


class TasksResponse(BaseModel):
    """Response model for tasks endpoint."""
    tasks: List[TaskItem]


class MemorySearchItem(BaseModel):
    """Model for memory search results."""
    text: str
    relevance_score: float


class MemorySearchResponse(BaseModel):
    """Response model for memory search endpoint."""
    results: List[MemorySearchItem]