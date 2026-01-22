"""문서 관리 API 라우트"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.schemas import DocumentUploadResponse, DocumentMetadata
from src.retrievers.document_processor import DocumentProcessor
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 문서 처리기 인스턴스
doc_processor = DocumentProcessor()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    문서 업로드 및 벡터화
    
    - 지원 포맷: PDF, DOCX, TXT, MD
    - 자동 청킹 및 임베딩
    - Milvus에 벡터 저장
    - PostgreSQL에 메타데이터 저장
    """
    try:
        result = await doc_processor.process_upload(file)
        return DocumentUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DocumentMetadata])
async def list_documents():
    """업로드된 문서 목록"""
    try:
        documents = await doc_processor.list_documents()
        return documents
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """문서 삭제 (Milvus + PostgreSQL)"""
    try:
        await doc_processor.delete_document(document_id)
        return {"message": f"Document {document_id} deleted"}
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
