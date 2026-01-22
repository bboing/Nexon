"""Milvus 벡터 검색기"""
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
from src.models.embeddings import embedding_model
from config.settings import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class MilvusRetriever:
    """Milvus 벡터 DB 검색기"""
    
    def __init__(self):
        self.collection_name = settings.milvus_collection_name
        self.dimension = settings.milvus_dimension
        self._connect()
        self._ensure_collection()
    
    def _connect(self):
        """Milvus 연결"""
        try:
            connections.connect(
                alias="default",
                host=settings.milvus_host,
                port=settings.milvus_port
            )
            logger.info(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")
        except Exception as e:
            logger.error(f"Milvus connection failed: {e}")
            raise
    
    def _ensure_collection(self):
        """컬렉션 생성 (없으면)"""
        if not utility.has_collection(self.collection_name):
            # 스키마 정의
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="chunk_index", dtype=DataType.INT64),
            ]
            
            schema = CollectionSchema(fields=fields, description="Document embeddings")
            collection = Collection(name=self.collection_name, schema=schema)
            
            # 인덱스 생성 (HNSW - 빠른 검색)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 200}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info(f"Created collection: {self.collection_name}")
        
        self.collection = Collection(self.collection_name)
        self.collection.load()
    
    async def insert(self, chunks: List[Dict]) -> List[str]:
        """
        벡터 삽입
        
        chunks: [
            {
                "id": "uuid",
                "content": "텍스트",
                "document_id": "문서ID",
                "chunk_index": 0
            },
            ...
        ]
        """
        # 임베딩 생성
        contents = [chunk["content"] for chunk in chunks]
        embeddings = embedding_model.embed_texts(contents)
        
        # 데이터 준비
        entities = [
            [chunk["id"] for chunk in chunks],  # id
            embeddings,  # embedding
            contents,  # content
            [chunk["document_id"] for chunk in chunks],  # document_id
            [chunk["chunk_index"] for chunk in chunks],  # chunk_index
        ]
        
        # 삽입
        self.collection.insert(entities)
        self.collection.flush()
        
        logger.info(f"Inserted {len(chunks)} vectors into Milvus")
        return [chunk["id"] for chunk in chunks]
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """유사도 검색"""
        # 쿼리 임베딩
        query_embedding = embedding_model.embed_text(query)
        
        # 검색
        search_params = {"metric_type": "COSINE", "params": {"ef": 100}}
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["content", "document_id", "chunk_index"]
        )
        
        # 결과 포맷팅
        retrieved = []
        for hits in results:
            for hit in hits:
                retrieved.append({
                    "content": hit.entity.get("content"),
                    "score": float(hit.score),
                    "metadata": {
                        "document_id": hit.entity.get("document_id"),
                        "chunk_index": hit.entity.get("chunk_index"),
                    }
                })
        
        return retrieved
    
    async def delete_by_document(self, document_id: str):
        """문서의 모든 벡터 삭제"""
        expr = f'document_id == "{document_id}"'
        self.collection.delete(expr)
        logger.info(f"Deleted vectors for document: {document_id}")
    
    async def get_stats(self) -> Dict:
        """통계 정보"""
        stats = self.collection.num_entities
        return {
            "collection_name": self.collection_name,
            "total_vectors": stats,
            "dimension": self.dimension
        }
