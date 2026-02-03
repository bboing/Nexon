"""
PostgreSQL 세션 관리
SQLAlchemy 엔진 및 세션 팩토리
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,  # 연결 유지 확인
    pool_size=10,  # 커넥션 풀 크기
    max_overflow=20,  # 최대 초과 연결 수
    pool_recycle=3600,  # 1시간마다 커넥션 재생성
    echo=True,  # SQL 로그 출력 (개발 시 True로 변경 가능)
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator:
    """
    FastAPI Dependency로 사용할 DB 세션
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화
    GraphRAG 필수 테이블만 생성 (users, maple_dictionary)
    """
    from .base import Base
    from .models import user, maple_dictionary  # 필수 모델만 import
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        logger.info(f"   Tables: {list(Base.metadata.tables.keys())}")
        logger.info("   - users: 사용자 정보")
        logger.info("   - maple_dictionary: 용어 사전 (엔티티 추출)")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
