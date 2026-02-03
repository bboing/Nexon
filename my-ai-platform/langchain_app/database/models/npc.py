"""
NPC 모델
메이플스토리 NPC 정보 저장
"""
from sqlalchemy import Column, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database.base import Base
import uuid


class NPC(Base):
    """
    NPC 테이블
    
    용도:
    - NPC 기본 정보 저장
    - RAG 검색용 메타데이터
    - 프롬프트 주입용 instruction
    """
    __tablename__ = "npcs"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # NPC 기본 정보
    npc_name = Column(String(100), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)  # 거주 도시
    instruction = Column(Text, nullable=False)  # NPC 설정 (System 프롬프트용)
    
    # 검색용 필드
    description = Column(Text, nullable=True)  # 임베딩용 요약
    keywords = Column(Text, nullable=True)  # 검색 키워드 (쉼표 구분)
    
    # 추가 메타데이터 (JSONB로 유연하게)
    # 주의: 'metadata'는 SQLAlchemy 예약어이므로 'extra_data' 사용
    extra_data = Column(JSONB, nullable=True)
    # 예: {"role": "상인", "quests": ["quest_id_1"], "items": ["item_id_1"]}
    
    # 대화 예시 (학습 데이터)
    sample_conversations = Column(JSONB, nullable=True)
    # 예: [{"input": "질문", "output": "답변"}, ...]
    
    # 상태 정보
    is_active = Column(String(10), default="true")  # NPC 활성화 여부
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 복합 인덱스 (city + npc_name 조합 검색 최적화)
    __table_args__ = (
        Index('idx_city_npc', city, npc_name),
    )
    
    def __repr__(self):
        return f"<NPC(name={self.npc_name}, city={self.city})>"
    
    def to_dict(self):
        """딕셔너리 변환"""
        return {
            "id": str(self.id),
            "npc_name": self.npc_name,
            "city": self.city,
            "instruction": self.instruction,
            "description": self.description,
            "keywords": self.keywords,
            "extra_data": self.extra_data,
            "sample_conversations": self.sample_conversations,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
