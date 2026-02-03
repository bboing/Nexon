"""
LangChain AI Platform - FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
# 임시로 모든 라우터 비활성화 (LangChain v0.3 마이그레이션 중)
# from api.routers import chat, rag, documents, agents, router

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
    logger.info(f"Ollama: {settings.OLLAMA_BASE_URL}")
    logger.info(f"PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    logger.info(f"Milvus: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    logger.info(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
    # DB 테이블 초기화
    logger.info("🗄️ Initializing database tables...")
    try:
        from database.session import init_db
        init_db()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    yield
    
    # 종료 시 실행
    logger.info("👋 LangChain AI Platform 종료...")


# FastAPI 앱 생성 (lifespan 연결!)
app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
# NPC Chat API는 제거됨 (npcs 테이블 불필요)

# TODO: LangChain v0.3 마이그레이션 중
# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
# app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
# app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
# app.include_router(router.router, prefix="/api/router", tags=["Router"])


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
            "ollama": settings.OLLAMA_BASE_URL,
            "postgres": f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}",
            "milvus": f"{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
            "redis": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}"
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
