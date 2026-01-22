"""대화 체인 - 메모리 기반 채팅"""
from langchain.chains import ConversationChain as LCConversationChain
from langchain.memory import ConversationBufferMemory
from src.models.llm import llm_model
from src.models.langfuse_callback import get_langfuse_handler
from typing import Dict
import redis.asyncio as redis
from config.settings import settings
import json


class ConversationChain:
    """대화 체인 with Redis 메모리"""
    
    def __init__(self):
        self.llm = llm_model.llm
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def _get_memory(self, session_id: str) -> ConversationBufferMemory:
        """세션별 메모리 로드"""
        memory = ConversationBufferMemory(return_messages=True)
        
        if self.redis_client:
            try:
                # Redis에서 대화 기록 로드
                history = await self.redis_client.get(f"chat:{session_id}")
                if history:
                    history_data = json.loads(history)
                    for msg in history_data:
                        if msg["role"] == "user":
                            memory.chat_memory.add_user_message(msg["content"])
                        else:
                            memory.chat_memory.add_ai_message(msg["content"])
            except Exception as e:
                print(f"Memory load error: {e}")
        
        return memory
    
    async def _save_memory(self, session_id: str, memory: ConversationBufferMemory):
        """메모리를 Redis에 저장"""
        if self.redis_client:
            try:
                messages = []
                for msg in memory.chat_memory.messages:
                    messages.append({
                        "role": "user" if msg.type == "human" else "assistant",
                        "content": msg.content
                    })
                
                await self.redis_client.set(
                    f"chat:{session_id}",
                    json.dumps(messages),
                    ex=86400  # 24시간 TTL
                )
            except Exception as e:
                print(f"Memory save error: {e}")
    
    async def run(self, message: str, session_id: str, model: str = None) -> str:
        """대화 실행"""
        # 세션별 메모리 로드
        memory = await self._get_memory(session_id)
        
        # LLM 선택
        llm = llm_model.get_llm(model) if model else self.llm
        
        # Langfuse 콜백 준비
        callbacks = []
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
        
        # 대화 체인 생성
        chain = LCConversationChain(
            llm=llm,
            memory=memory,
            verbose=True
        )
        
        # 실행 (Langfuse Cloud로 자동 추적)
        response = chain.predict(
            input=message,
            callbacks=callbacks
        )
        
        # 메모리 저장
        await self._save_memory(session_id, memory)
        
        return response
    
    async def clear_history(self, session_id: str):
        """대화 기록 삭제"""
        if self.redis_client:
            await self.redis_client.delete(f"chat:{session_id}")
