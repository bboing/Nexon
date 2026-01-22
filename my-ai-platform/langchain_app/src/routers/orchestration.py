from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import httpx

class IntelligentRouter:
    def __init__(self):
        # 작은 분류 모델 (빠른 응답)
        self.classifier = ChatOllama(
            model="llama3.2:1b",  # 작은 모델로 빠르게 분류
            base_url="http://host.docker.internal:11434"
        )
        
        # 라우팅 대상
        self.routes = {
            "game_npc": {
                "description": "메이플스토리 NPC 대화, 게임 관련 질문",
                "handler": self.handle_ollama
            },
            "rag_search": {
                "description": "문서 검색, 정보 조회, 데이터베이스 질의",
                "handler": self.handle_langchain_rag
            },
            "complex_reasoning": {
                "description": "복잡한 추론, 수학 문제, 코드 생성",
                "handler": self.handle_external_api
            },
            "mcp_tools": {
                "description": "웹 검색, 파일 작업, API 호출 등 도구 사용",
                "handler": self.handle_mcp
            }
        }
    
    async def route(self, user_message: str) -> dict:
        """메인 라우팅 함수"""
        # 1. 의미 분류
        route_name = await self.classify(user_message)
        
        # 2. 해당 핸들러 호출
        handler = self.routes[route_name]["handler"]
        response = await handler(user_message)
        
        return {
            "route": route_name,
            "response": response
        }
    
    async def classify(self, message: str) -> str:
        """LLM으로 의미 분류"""
        prompt = f"""
        다음 사용자 메시지를 분석하여 가장 적합한 처리 방법을 선택하세요.
        
        선택지:
        - game_npc: 메이플스토리 NPC 대화, 게임 관련
        - rag_search: 문서 검색, 정보 조회
        - complex_reasoning: 복잡한 추론, 수학, 코드
        - mcp_tools: 웹 검색, 외부 도구 사용
        
        사용자 메시지: {message}
        
        응답 (하나만): 
        """
        
        result = await self.classifier.ainvoke(prompt)
        route = result.content.strip().lower()
        
        # 기본값
        if route not in self.routes:
            route = "game_npc"
        
        return route
    
    async def handle_ollama(self, message: str) -> str:
        """로컬 Ollama (파인튜닝된 모델)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "llama-game-npc",  # 파인튜닝된 모델
                    "prompt": message,
                    "stream": False
                }
            )
            return response.json()["response"]
    
    async def handle_langchain_rag(self, message: str) -> str:
        """LangChain RAG (Milvus 검색)"""
        # 기존 RAG 체인 호출
        from src.chains.rag_chain import rag_chain
        result = await rag_chain.ainvoke({"query": message})
        return result["answer"]
    
    async def handle_external_api(self, message: str) -> str:
        """외부 API (GPT-4, Claude 등)"""
        # OpenAI API 호출
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": message}]
                }
            )
            return response.json()["choices"][0]["message"]["content"]
    
    async def handle_mcp(self, message: str) -> str:
        """MCP (Model Context Protocol) 도구 사용"""
        # LangChain Tools 또는 MCP 서버 호출
        from langchain.agents import AgentExecutor
        # ... MCP 통합 로직
        pass