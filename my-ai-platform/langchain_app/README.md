# LangChain Application

LangChain + LangGraph + Ollama + Milvus 기반 AI 애플리케이션

## 🏗️ 아키텍처

```
FastAPI (api/)
    ↓
LangChain/LangGraph (src/)
    ↓
┌──────────┬──────────┬──────────┐
│ Ollama   │ Milvus   │ Postgres │
│ (LLM)    │ (Vector) │ (RDB)    │
└──────────┴──────────┴──────────┘
```

## 📁 디렉토리 구조

```
langchain_app/
├── api/                    # FastAPI 애플리케이션
│   ├── main.py            # 메인 앱
│   ├── routes/            # API 엔드포인트
│   │   ├── chat.py        # 채팅
│   │   ├── rag.py         # RAG
│   │   ├── documents.py   # 문서 관리
│   │   └── agents.py      # 에이전트
│   └── schemas/           # Pydantic 스키마
│
├── src/                   # 핵심 로직
│   ├── chains/            # LangChain 체인
│   │   ├── conversation.py    # 대화 체인
│   │   └── rag_chain.py       # RAG 체인
│   │
│   ├── agents/            # LangGraph 에이전트
│   │   └── research_agent.py  # 연구 에이전트
│   │
│   ├── retrievers/        # 검색기
│   │   ├── milvus_retriever.py      # Milvus 벡터 검색
│   │   └── document_processor.py    # 문서 처리
│   │
│   └── models/            # 모델 래퍼
│       ├── llm.py         # Ollama LLM
│       └── embeddings.py  # 임베딩 모델
│
├── config/
│   └── settings.py        # 설정 관리
│
├── tests/                 # 테스트
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 로컬 개발

### 1. 가상환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

환경 변수는 Docker Compose에서 자동으로 주입됩니다.
로컬 개발 시에는 `.env` 파일을 생성하세요:

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aiplatform
POSTGRES_USER=admin
POSTGRES_PASSWORD=changeme

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=changeme
```

### 4. 서버 실행

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서: http://localhost:8000/docs

## 🧪 테스트

```bash
# 전체 테스트
pytest

# 특정 테스트
pytest tests/test_rag.py

# 커버리지
pytest --cov=src tests/
```

## 📝 새 기능 추가하기

### 1. 새 체인 추가

```python
# src/chains/my_chain.py

from langchain.chains import LLMChain
from src.models.llm import llm_model

class MyChain:
    def __init__(self):
        self.llm = llm_model.llm
    
    async def run(self, input_data):
        # 구현
        pass
```

### 2. API 엔드포인트 추가

```python
# api/routes/my_route.py

from fastapi import APIRouter
router = APIRouter()

@router.post("/")
async def my_endpoint():
    # 구현
    pass
```

```python
# api/main.py에 라우터 등록

from api.routes import my_route
app.include_router(my_route.router, prefix="/api/my", tags=["My"])
```

### 3. LangGraph 에이전트 추가

```python
# src/agents/my_agent.py

from langgraph.graph import StateGraph, END
from typing import TypedDict

class MyState(TypedDict):
    # 상태 정의
    pass

class MyAgent:
    def _build_graph(self):
        workflow = StateGraph(MyState)
        # 노드 및 엣지 추가
        return workflow.compile()
    
    async def execute(self, task: str):
        # 구현
        pass
```

## 🔍 디버깅

### LangSmith 연동

```bash
# .env에 추가
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=ai-platform
```

모든 LangChain 호출이 LangSmith에 자동 로깅됩니다.

### 로그 레벨 조정

```python
# config/settings.py
log_level: str = "debug"  # info, debug, warning, error
```

## 🐳 Docker 빌드

```bash
docker build -t langchain-api .
docker run -p 8000:8000 --env-file .env langchain-api
```

## 📚 참고 자료

- [LangChain 문서](https://python.langchain.com/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Milvus Python SDK](https://milvus.io/docs/v2.3.x/install_pymilvus.md)
