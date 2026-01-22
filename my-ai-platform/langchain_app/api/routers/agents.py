"""LangGraph 에이전트 API 라우트"""
from fastapi import APIRouter, HTTPException
from api.schemas import AgentRequest, AgentResponse
from src.agents.research_agent import ResearchAgent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 에이전트 인스턴스
research_agent = ResearchAgent()


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """
    LangGraph 에이전트 실행
    
    - 멀티 에이전트 워크플로우
    - 상태 기반 의사결정
    - 조건부 분기
    """
    try:
        # 에이전트 타입에 따라 분기
        if request.agent_type == "research":
            result = await research_agent.execute(
                task=request.task,
                session_id=request.session_id
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        return AgentResponse(**result)
        
    except Exception as e:
        logger.error(f"Agent execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_agent_types():
    """사용 가능한 에이전트 타입 목록"""
    return {
        "agents": [
            {
                "type": "research",
                "description": "정보 조사 및 분석 에이전트",
                "capabilities": ["web_search", "document_analysis", "summarization"]
            }
        ]
    }
