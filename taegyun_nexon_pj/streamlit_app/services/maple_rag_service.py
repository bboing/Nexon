"""
Maple RAG Service
기존 langchain_app의 RAG 로직을 Streamlit용으로 래핑
"""
import asyncio
from typing import Dict, Any
from langchain_groq import ChatGroq

from database.session import get_async_session
from src.retrievers.hybrid_searcher import HybridSearcher
from src.generators.answer_generator import AnswerGenerator


class MapleRAGService:
    """
    Streamlit용 RAG 서비스
    
    기존 langchain_app의 비동기 로직을 동기적으로 래핑
    """
    
    def __init__(self, groq_api_key: str):
        """
        Args:
            groq_api_key: Groq API Key
        """
        self.groq_api_key = groq_api_key
        
        # Groq LLM 초기화
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",  # 또는 "llama-3.1-70b-versatile"
            api_key=groq_api_key,
            temperature=0.3
        )
    
    def query(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        질문에 답변 (동기)
        
        Args:
            question: 사용자 질문
            max_results: 최대 검색 결과 수
            
        Returns:
            {
                "answer": str,
                "sources": List[str],
                "confidence": float,
                "search_results": List[Dict]
            }
        """
        # 비동기 로직을 동기로 실행
        return asyncio.run(self._async_query(question, max_results))
    
    async def _async_query(self, question: str, max_results: int) -> Dict[str, Any]:
        """
        실제 비동기 쿼리 로직
        """
        # DB 세션 생성
        async for session in get_async_session():
            # 1. Hybrid Search
            searcher = HybridSearcher(
                db=session,
                use_milvus=True,
                use_neo4j=True,
                use_router=True,
                verbose=False
            )
            
            search_results = await searcher.search(
                query=question,
                limit=max_results
            )
            
            # 2. Answer Generation
            generator = AnswerGenerator(
                llm=self.llm,
                verbose=False
            )
            
            answer_result = await generator.generate(
                query=question,
                search_results=search_results,
                max_context_items=max_results
            )
            
            # 3. 결과 반환
            return {
                "answer": answer_result["answer"],
                "sources": answer_result["sources"],
                "confidence": answer_result["confidence"],
                "search_results": search_results
            }
