"""
LangChain AI Platform - 설정 관리
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    """config 설정"""
    base_path=Path(__file__).resolve().parent.parent.parent
    env_path=base_path / ".env"

    model_config= SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extre="ignore"
    )

    """애플리케이션 설정"""
    # Ollama 설정
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL: str 
    
    # PostgreSQL 설정
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str


    # Milvus 설정
    MILVUS_HOST: str
    MILVUS_PORT: int
    MILVUS_METRIC_PORT: int
    MILBUS_COLLECTION_NAME: str
    MILVUS_DIMENSION: int = 384  # sentence-transformers/all-MiniLM-L6-v2 기본값
    
    # Redis 설정
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int

    # Langfuse 설정 (LLM Observability - Cloud 사용)
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_BASE_URL: str
    LANGFUSE_ENABLED: bool
    
    # API 설정
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    log_level: str = "info"
    
    # RAG 설정
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5
    
    # 임베딩 모델
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def async_postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
    



# 싱글톤 인스턴스
settings = Settings()
