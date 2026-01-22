"""RAG 체인 - 검색 증강 생성"""
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from src.models.llm import llm_model
from src.models.langfuse_callback import get_langfuse_handler
from src.retrievers.milvus_retriever import MilvusRetriever
from typing import Dict, List
import time


class RAGChain:
    """RAG (Retrieval-Augmented Generation) 체인"""
    
    def __init__(self):
        self.llm = llm_model.llm
        self.retriever = MilvusRetriever()
        
        # RAG 프롬프트 템플릿
        self.prompt_template = PromptTemplate(
            template="""다음 컨텍스트를 바탕으로 질문에 답변해주세요.
컨텍스트에 답변이 없다면, "주어진 정보로는 답변할 수 없습니다"라고 말해주세요.

컨텍스트:
{context}

질문: {question}

답변:""",
            input_variables=["context", "question"]
        )
    
    async def query(self, question: str, top_k: int = 5, session_id: str = None) -> Dict:
        """RAG 쿼리 실행"""
        start_time = time.time()
        
        # 1. 관련 문서 검색 (Milvus)
        search_start = time.time()
        retrieved_docs = await self.retriever.search(question, top_k=top_k)
        search_time = int((time.time() - search_start) * 1000)
        
        # 2. 컨텍스트 구성
        context = "\n\n".join([
            f"[문서 {i+1}] {doc['content']}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # 3. LLM으로 답변 생성 (Langfuse 추적)
        gen_start = time.time()
        prompt = self.prompt_template.format(context=context, question=question)
        
        # Langfuse 콜백
        callbacks = []
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
        
        answer = self.llm.predict(prompt, callbacks=callbacks)
        gen_time = int((time.time() - gen_start) * 1000)
        
        # 4. 소스 정보 구성
        sources = [
            {
                "content": doc["content"][:200] + "...",  # 처음 200자만
                "score": doc["score"],
                "metadata": doc.get("metadata", {})
            }
            for doc in retrieved_docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
            "search_time_ms": search_time,
            "generation_time_ms": gen_time,
            "total_time_ms": int((time.time() - start_time) * 1000)
        }
    
    async def get_stats(self) -> Dict:
        """RAG 통계"""
        return await self.retriever.get_stats()
