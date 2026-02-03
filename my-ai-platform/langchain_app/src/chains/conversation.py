"""대화 체인 - 메모리 기반 채팅"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
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
    
    async def _get_history(self, session_id: str) -> ChatMessageHistory:
        """세션별 메시지 히스토리 로드"""
        history = ChatMessageHistory()
        
        if self.redis_client:
            try:
                # Redis에서 대화 기록 로드
                history_json = await self.redis_client.get(f"chat:{session_id}")
                if history_json:
                    history_data = json.loads(history_json)
                    for msg in history_data:
                        if msg["role"] == "user":
                            history.add_user_message(msg["content"])
                        else:
                            history.add_ai_message(msg["content"])
            except Exception as e:
                print(f"Memory load error: {e}")
        
        return history
    
    async def _save_history(self, session_id: str, history: ChatMessageHistory):
        """히스토리를 Redis에 저장"""
        if self.redis_client:
            try:
                messages = []
                for msg in history.messages:
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
        """대화 실행 (LangChain v0.3 LCEL 방식)"""
        # 세션별 히스토리 로드
        history = await self._get_history(session_id)
        
        # LLM 선택
        llm = llm_model.get_llm(model) if model else self.llm
        
        # Langfuse 콜백 준비
        callbacks = []
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
        
        # 프롬프트 템플릿
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Have a conversation with the user."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        # 체인 생성
        chain = prompt | llm
        
        # 실행
        response = chain.invoke(
            {
                "history": history.messages,
                "input": message
            },
            config={"callbacks": callbacks}
        )
        
        # 히스토리에 추가
        history.add_user_message(message)
        history.add_ai_message(response.content)
        
        # Redis에 저장
        await self._save_history(session_id, history)
        
        return response.content
    
    async def clear_history(self, session_id: str):
        """대화 기록 삭제"""
        if self.redis_client:
            await self.redis_client.delete(f"chat:{session_id}")
