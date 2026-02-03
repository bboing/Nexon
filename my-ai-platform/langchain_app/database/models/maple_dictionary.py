from sqlalchemy import Column, String, Text, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func
from database.base import Base
import uuid
import enum

class CategoryEnum(str, enum.Enum):
    ITEM = "ITEM"
    BOSS = "BOSS"
    NPC = "NPC"
    MAP = "MAP"
    QUEST = "QUEST"
    SKILL = "SKILL"
    MONSTER = "MONSTER"

class MapleDictionary(Base):
    __tablename__ = "maple_dictionary"
    
    # 1. 고유 식별자: DB가 생성하므로 nullable=False 유지
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 2. 공식 명칭: 시스템의 핵심 키이므로 절대 비울 수 없음
    canonical_name = Column(String(200), unique=True, nullable=False, index=True)
    
    # 3. 줄임말/은어: 없을 수도 있으므로 True
    synonyms = Column(ARRAY(String), nullable=True, server_default='{}')
    
    # 4. 카테고리: 데이터 분류의 핵심이므로 필수
    category = Column(Enum(CategoryEnum), nullable=False, index=True)
    
    # 5. 설명 (수정 포인트): 임베딩 전에는 비어있을 수 있으므로 True로 변경
    description = Column(Text, nullable=True) 
    
    # 6. 상세 정보 (수정 포인트): 초기 데이터 로드 시 빈 객체일 수 있으므로 True
    # server_default를 통해 DB 레벨에서도 기본 빈 객체({})를 보장하면 더 안전해.
    # 주의: 'metadata'는 SQLAlchemy 예약어이므로 'detail_data' 사용
    detail_data = Column(JSONB, nullable=True, server_default='{}')
    
    # 7. 검색 벡터: 검색 엔진 최적화용 (Nullable 유지)
    search_vector = Column(Text, nullable=True)
    
    # 8. 타임스탬프: DB가 자동 관리
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        Index('idx_synonyms_gin', synonyms, postgresql_using='gin'),
        Index('idx_detail_data_gin', detail_data, postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<MapleDictionary(name={self.canonical_name}, category={self.category})>"
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            "id": str(self.id),
            "canonical_name": self.canonical_name,
            "synonyms": self.synonyms,
            "category": self.category.value,
            "description": self.description,
            "detail_data": self.detail_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
