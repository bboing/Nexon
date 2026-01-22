"""임베딩 모델 관리"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import settings


class EmbeddingModel:
    """임베딩 모델 싱글톤"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={'device': 'cpu'},  # GPU 사용 시 'cuda'로 변경
                encode_kwargs={'normalize_embeddings': True}
            )
        return cls._instance
    
    @property
    def embeddings(self):
        return self._embeddings
    
    def embed_text(self, text: str):
        """단일 텍스트 임베딩"""
        return self._embeddings.embed_query(text)
    
    def embed_texts(self, texts: list):
        """여러 텍스트 임베딩"""
        return self._embeddings.embed_documents(texts)


# 싱글톤 인스턴스
embedding_model = EmbeddingModel()
