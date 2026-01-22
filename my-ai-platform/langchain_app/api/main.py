"""
LangChain AI Platform - FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from api.routers import chat, rag, documents, agents, router

# 로깅 설정
logging.basicConfig(
    level=settings.log_level.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("🚀 LangChain AI Platform 시작...")
    logger.info(f"Ollama: {settings.ollama_base_url}")
    logger.info(f"PostgreSQL: {settings.postgres_host}:{settings.postgres_port}")
    logger.info(f"Milvus: {settings.milvus_host}:{settings.milvus_port}")
    logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")
    
    yield
    
    # 종료 시 실행
    logger.info("👋 LangChain AI Platform 종료...")


# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(router.router, prefix="/api/router", tags=["router"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 LangChain AI Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "services": {
            "ollama": settings.ollama_base_url,
            "postgres": f"{settings.postgres_host}:{settings.postgres_port}",
            "milvus": f"{settings.milvus_host}:{settings.milvus_port}",
            "redis": f"{settings.redis_host}:{settings.redis_port}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level
    )
