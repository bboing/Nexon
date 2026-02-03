"""
NPC CRUD 작업
"""
from sqlalchemy.orm import Session
from database.models.npc import NPC
from typing import List, Optional
import logging
import json

logger = logging.getLogger(__name__)


def create_npc(
    db: Session,
    npc_name: str,
    city: str,
    instruction: str,
    description: Optional[str] = None,
    keywords: Optional[str] = None,
    extra_data: Optional[dict] = None,
    sample_conversations: Optional[list] = None,
) -> NPC:
    """
    NPC 생성
    
    Args:
        db: DB 세션
        npc_name: NPC 이름
        city: 거주 도시
        instruction: NPC 설정 (System 프롬프트용)
        description: 요약 설명
        keywords: 검색 키워드
        extra_data: 추가 정보 (JSONB)
        sample_conversations: 대화 예시
    
    Returns:
        생성된 NPC 객체
    """
    try:
        npc = NPC(
            npc_name=npc_name,
            city=city,
            instruction=instruction,
            description=description or instruction[:200],  # 기본값: instruction 앞부분
            keywords=keywords,
            extra_data=extra_data or {},
            sample_conversations=sample_conversations or [],
            is_active="true",
        )
        db.add(npc)
        db.commit()
        db.refresh(npc)
        logger.info(f"✅ NPC created: {npc.npc_name} ({npc.city})")
        return npc
    except Exception as e:
        logger.error(f"❌ Failed to create NPC: {e}")
        db.rollback()
        raise


def get_npc(db: Session, npc_name: str, city: Optional[str] = None) -> Optional[NPC]:
    """
    NPC 조회 (이름)
    
    Args:
        db: DB 세션
        npc_name: NPC 이름
        city: 도시 (선택, 동명이인 방지)
    
    Returns:
        NPC 객체 또는 None
    """
    query = db.query(NPC).filter(NPC.npc_name == npc_name)
    
    if city:
        query = query.filter(NPC.city == city)
    
    return query.first()


def get_npc_by_id(db: Session, npc_id: str) -> Optional[NPC]:
    """NPC 조회 (ID)"""
    return db.query(NPC).filter(NPC.id == npc_id).first()


def get_npcs_by_city(db: Session, city: str) -> List[NPC]:
    """특정 도시의 NPC 목록"""
    return db.query(NPC).filter(NPC.city == city).all()


def get_all_npcs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    only_active: bool = True
) -> List[NPC]:
    """
    NPC 목록 조회
    
    Args:
        db: DB 세션
        skip: 건너뛸 개수
        limit: 최대 개수
        only_active: 활성 NPC만 조회
    
    Returns:
        NPC 리스트
    """
    query = db.query(NPC)
    
    if only_active:
        query = query.filter(NPC.is_active == "true")
    
    return query.order_by(NPC.npc_name).offset(skip).limit(limit).all()


def search_npcs(db: Session, keyword: str, limit: int = 10) -> List[NPC]:
    """
    NPC 검색 (키워드)
    
    Args:
        db: DB 세션
        keyword: 검색 키워드
        limit: 최대 개수
    
    Returns:
        NPC 리스트
    """
    return db.query(NPC).filter(
        (NPC.npc_name.ilike(f"%{keyword}%")) |
        (NPC.instruction.ilike(f"%{keyword}%")) |
        (NPC.keywords.ilike(f"%{keyword}%"))
    ).limit(limit).all()


def update_npc(
    db: Session,
    npc_name: str,
    **kwargs
) -> Optional[NPC]:
    """
    NPC 업데이트
    
    Args:
        db: DB 세션
        npc_name: NPC 이름
        **kwargs: 업데이트할 필드들
    
    Returns:
        업데이트된 NPC 객체
    """
    try:
        npc = get_npc(db, npc_name)
        if not npc:
            logger.warning(f"NPC not found: {npc_name}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(npc, key):
                setattr(npc, key, value)
        
        db.commit()
        db.refresh(npc)
        logger.info(f"✅ NPC updated: {npc_name}")
        return npc
    except Exception as e:
        logger.error(f"❌ Failed to update NPC: {e}")
        db.rollback()
        raise


def delete_npc(db: Session, npc_name: str) -> bool:
    """
    NPC 삭제
    
    Args:
        db: DB 세션
        npc_name: NPC 이름
    
    Returns:
        성공 여부
    """
    try:
        npc = get_npc(db, npc_name)
        if not npc:
            logger.warning(f"NPC not found: {npc_name}")
            return False
        
        db.delete(npc)
        db.commit()
        logger.info(f"✅ NPC deleted: {npc_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete NPC: {e}")
        db.rollback()
        raise


def import_from_json(db: Session, json_path: str) -> int:
    """
    JSON 파일에서 NPC 대량 import
    
    Args:
        db: DB 세션
        json_path: maple_npc.json 경로
    
    Returns:
        import된 NPC 수
    """
    import json
    from pathlib import Path
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = 0
        for item in data:
            # 이미 존재하는지 확인
            existing = get_npc(db, item['NPC_Name'], item['City'])
            if existing:
                logger.info(f"⚠️  NPC already exists: {item['NPC_Name']}")
                continue
            
            # 새로 생성
            npc = NPC(
                npc_name=item['NPC_Name'],
                city=item['City'],
                instruction=item['instruction'],
                description=item['instruction'][:200],  # 앞 200자
                keywords=f"{item['NPC_Name']},{item['City']}",
                extra_data={
                    "sample_input": item.get('input'),
                    "sample_output": item.get('output'),
                },
                sample_conversations=[{
                    "input": item.get('input'),
                    "output": item.get('output')
                }] if item.get('input') else [],
                is_active="true"
            )
            db.add(npc)
            count += 1
        
        db.commit()
        logger.info(f"✅ Imported {count} NPCs from {json_path}")
        return count
        
    except Exception as e:
        logger.error(f"❌ Failed to import NPCs: {e}")
        db.rollback()
        raise


def get_cities(db: Session) -> List[str]:
    """모든 도시 목록 조회"""
    result = db.query(NPC.city).distinct().all()
    return [r[0] for r in result]


def get_npc_count_by_city(db: Session) -> dict:
    """도시별 NPC 수 조회"""
    from sqlalchemy import func as sql_func
    
    result = db.query(
        NPC.city,
        sql_func.count(NPC.id).label('count')
    ).group_by(NPC.city).all()
    
    return {city: count for city, count in result}
