"""채팅 API 라우트"""
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from src.chains.conversation import ConversationChain
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 대화 체인 인스턴스 (싱글톤)
conversation_chain = ConversationChain()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    기본 채팅 엔드포인트
    
    - 대화 메모리 유지
    - Ollama LLM 사용
    """
    try:
        # 세션 ID가 없으면 생성
        session_id = request.session_id or str(uuid.uuid4())
        
        # 대화 실행
        response = await conversation_chain.run(
            message=request.message,
            session_id=session_id,
            model=request.model
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            model=request.model
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def clear_chat_history(session_id: str):
    """대화 기록 삭제"""
    try:
        await conversation_chain.clear_history(session_id)
        return {"message": f"Session {session_id} cleared"}
    except Exception as e:
        logger.error(f"Clear history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
