# my-ai-platform/langchain_app/api/routes/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.routers.orchestration import IntelligentRouter

router = APIRouter(prefix="/api/router", tags=["Intelligent Router"])

class RouterRequest(BaseModel):
    message: str

@router.post("/query")
async def intelligent_route(request: RouterRequest):
    """지능형 라우팅"""
    orchestration = IntelligentRouter()
    result = await orchestration.route(request.message)
    
    return {
        "route_taken": result["route"],
        "response": result["response"],
        "timestamp": datetime.now().isoformat()
    }