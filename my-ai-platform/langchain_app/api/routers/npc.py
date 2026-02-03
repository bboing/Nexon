"""
NPC Chat API
메이플스토리 NPC와 대화하는 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from database.crud import npc as npc_crud
from database.schemas.npc_dto import (
    NPCChatRequest,
    NPCChatResponse,
    NPCResponse,
    NPCListResponse,
    NPCCreate
)
from src.models.llm import llm_model
from typing import List, Optional
import time
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=NPCChatResponse)
async def npc_chat(
    request: NPCChatRequest,
    db: Session = Depends(get_db)
):
    """
    NPC와 대화
    
    프롬프트 주입 방식:
    1. DB에서 NPC 정보 조회
    2. System 프롬프트에 NPC 설정 주입
    3. LLM 호출
    """
    start_time = time.time()
    
    # 1. NPC 조회
    npc = npc_crud.get_npc(db, request.npc_name, request.city)
    
    if not npc:
        raise HTTPException(
            status_code=404,
            detail=f"NPC '{request.npc_name}' not found"
        )
    
    # 2. System 프롬프트 구성 (학습 데이터와 동일한 형식!)
    system_prompt = f"당신은 '{npc.city}'에 거주하는 NPC '{npc.npc_name}'입니다. {npc.instruction}"
    
    # 3. LLM 호출
    try:
        llm = llm_model.get_llm(temperature=0.7)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]
        
        # Ollama 직접 호출 (langchain_ollama)
        response = await llm.ainvoke(
            f"{system_prompt}\n\n플레이어: {request.message}\nNPC:"
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return NPCChatResponse(
            npc_name=npc.npc_name,
            city=npc.city,
            message=request.message,
            response=response.content,
            session_id=request.session_id,
            rag_used=request.use_rag,
            latency_ms=latency_ms
        )
        
    except Exception as e:
        logger.error(f"❌ NPC chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=NPCListResponse)
async def list_npcs(
    city: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    NPC 목록 조회
    
    Args:
        city: 도시 필터 (선택)
        skip: 페이지네이션 offset
        limit: 페이지네이션 limit
    """
    if city:
        npcs = npc_crud.get_npcs_by_city(db, city)
    else:
        npcs = npc_crud.get_all_npcs(db, skip=skip, limit=limit)
    
    cities = npc_crud.get_cities(db)
    
    return NPCListResponse(
        npcs=[npc.to_dict() for npc in npcs],
        total=len(npcs),
        cities=cities
    )


@router.get("/{npc_name}", response_model=NPCResponse)
async def get_npc_info(
    npc_name: str,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    NPC 상세 정보 조회
    
    Args:
        npc_name: NPC 이름
        city: 도시 (선택)
    """
    npc = npc_crud.get_npc(db, npc_name, city)
    
    if not npc:
        raise HTTPException(
            status_code=404,
            detail=f"NPC '{npc_name}' not found"
        )
    
    return npc.to_dict()


@router.post("/import")
async def import_npcs(
    json_path: str = "/app/training/data/input_data/maple_npc.json",
    db: Session = Depends(get_db)
):
    """
    maple_npc.json에서 NPC 대량 import
    
    Args:
        json_path: JSON 파일 경로
    """
    try:
        count = npc_crud.import_from_json(db, json_path)
        return {
            "status": "success",
            "imported": count,
            "message": f"{count}개 NPC가 import되었습니다."
        }
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities/stats")
async def get_city_stats(db: Session = Depends(get_db)):
    """도시별 NPC 통계"""
    stats = npc_crud.get_npc_count_by_city(db)
    cities = npc_crud.get_cities(db)
    
    return {
        "total_cities": len(cities),
        "total_npcs": sum(stats.values()),
        "cities": stats
    }


@router.post("/search")
async def search_npcs(
    keyword: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    NPC 검색
    
    Args:
        keyword: 검색 키워드
        limit: 최대 결과 수
    """
    npcs = npc_crud.search_npcs(db, keyword, limit)
    
    return {
        "keyword": keyword,
        "results": [npc.to_dict() for npc in npcs],
        "count": len(npcs)
    }
