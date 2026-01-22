"""RAG API 라우트"""
from fastapi import APIRouter, HTTPException
from api.schemas import RAGQueryRequest, RAGQueryResponse
from src.chains.rag_chain import RAGChain
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# RAG 체인 인스턴스
rag_chain = RAGChain()


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """
    RAG 검색-생성 쿼리
    
    - Milvus에서 유사 문서 검색
    - Ollama로 답변 생성
    """
    try:
        result = await rag_chain.query(
            question=request.question,
            top_k=request.top_k,
            session_id=request.session_id
        )
        
        return RAGQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def rag_stats():
    """RAG 통계 정보"""
    try:
        stats = await rag_chain.get_stats()
        return stats
    except Exception as e:
        logger.error(f"RAG stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
