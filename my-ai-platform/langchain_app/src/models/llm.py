"""LLM 모델 관리 (Ollama)"""
from langchain_ollama import ChatOllama
from config.settings import settings


class LLMModel:
    """Ollama LLM 싱글톤"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._llm = ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.7,
            )
        return cls._instance
    
    def get_llm(self, model: str = None, temperature: float = 0.7):
        """LLM 인스턴스 반환 (커스텀 설정 가능)"""
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model or settings.OLLAMA_MODEL,
            temperature=temperature,
        )
    
    @property
    def llm(self):
        """기본 LLM 인스턴스"""
        return self._llm


# 싱글톤 인스턴스
llm_model = LLMModel()
