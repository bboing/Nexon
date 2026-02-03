"""Langfuse 콜백 핸들러 (Cloud 사용)"""
from typing import Optional
import logging

try:
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    CallbackHandler = None
    LANGFUSE_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)


class LangfuseManager:
    """Langfuse 콜백 매니저 싱글톤 (Cloud API 사용)"""
    
    _instance = None
    _callback_handler: Optional[CallbackHandler] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_langfuse()
        return cls._instance
    
    def _init_langfuse(self):
        """Langfuse Cloud 초기화"""
        if not LANGFUSE_AVAILABLE:
            logger.warning("⚠️ Langfuse SDK not available. Install with: pip install langfuse")
            return
            
        if not settings.LANGFUSE_ENABLED:
            logger.info("Langfuse disabled")
            return
        
        if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
            logger.warning("Langfuse keys not set. Observability disabled.")
            logger.warning("Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env")
            return
        
        try:
            self._callback_handler = CallbackHandler(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_BASE_URL
            )
            logger.info(f"✅ Langfuse Cloud initialized: {settings.LANGFUSE_BASE_URL}")
        except Exception as e:
            logger.error(f"❌ Langfuse initialization failed: {e}")
            self._callback_handler = None
    
    @property
    def handler(self) -> Optional[CallbackHandler]:
        """Langfuse 콜백 핸들러 반환"""
        return self._callback_handler
    
    @property
    def enabled(self) -> bool:
        """Langfuse 활성화 여부"""
        return self._callback_handler is not None


# 싱글톤 인스턴스
langfuse_manager = LangfuseManager()


def get_langfuse_handler() -> Optional[CallbackHandler]:
    """Langfuse 핸들러 반환 (헬퍼 함수)"""
    return langfuse_manager.handler
