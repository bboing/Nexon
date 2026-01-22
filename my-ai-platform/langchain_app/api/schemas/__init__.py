"""API 스키마 정의"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# 채팅 관련 스키마
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = "llama2"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    model: str


# RAG 관련 스키마
class RAGQueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    session_id: Optional[str] = None


class RAGSource(BaseModel):
    content: str
    score: float
    metadata: Dict[str, Any]


class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[RAGSource]
    session_id: Optional[str] = None


# 문서 관련 스키마
class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    chunk_count: int
    status: str


class DocumentMetadata(BaseModel):
    id: str
    title: str
    source: str
    file_type: str
    chunk_count: int
    uploaded_at: datetime


# 에이전트 관련 스키마
class AgentRequest(BaseModel):
    task: str
    agent_type: str = "research"
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    result: Any
    steps: List[Dict[str, Any]]
    execution_time_ms: int
    status: str
