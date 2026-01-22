# 🚀 LangChain AI Platform - 시작 가이드

## 📋 아키텍처 개요

```
┌──────────────────────────────────────────────────────┐
│  Integration Layer (후순위)                         │
│  └─ n8n (외부 시스템 연동, 비즈니스 자동화)         │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  API Layer                                           │
│  ├─ FastAPI (LangChain/LangGraph API)               │
│  └─ Nginx (리버스 프록시)                           │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  AI Orchestration Layer (핵심) 🌟                   │
│  ├─ LangGraph (멀티 에이전트 워크플로우)            │
│  └─ LangChain (RAG, 체인, 메모리)                   │
└──────────────────────────────────────────────────────┘
            ↓                           ↓
┌──────────────────┐        ┌──────────────────────────┐
│ Structured Data  │        │ Vector Data              │
│ PostgreSQL       │        │ Milvus                   │
│ ───────────────  │        │ ──────────────────────── │
│ • 사용자 정보    │        │ • 문서 임베딩            │
│ • 대화 히스토리  │        │ • 시맨틱 검색            │
│ • 메타데이터     │        │ • 유사도 검색            │
└──────────────────┘        └──────────────────────────┘
            ↓                           ↓
┌──────────────────────────────────────────────────────┐
│  Infrastructure                                      │
│  ├─ Ollama (LLM)                                    │
│  ├─ Redis (캐싱)                                    │
│  └─ Monitoring (Prometheus, Grafana, Loki)         │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 왜 이 구조인가?

### **PostgreSQL vs Milvus 역할 분리**

| 데이터 타입 | 저장소 | 이유 |
|-------------|--------|------|
| **사용자 정보, 대화 기록** | PostgreSQL | ACID 트랜잭션, 관계형 쿼리 |
| **문서 임베딩, 벡터** | Milvus | 대규모 벡터 검색 최적화 (백만+ 벡터) |
| **메타데이터** | PostgreSQL | 구조화된 쿼리 (JOIN, 집계) |
| **벡터 ID 매핑** | 양쪽 모두 | PostgreSQL에 Milvus ID 저장 |

### **LangChain이 중심인 이유**
- ✅ **AI 네이티브**: LLM, RAG, 에이전트에 최적화
- ✅ **코드 우선**: Git 버전 관리, pytest 테스트
- ✅ **확장성**: 복잡한 로직을 Python으로 표현
- ✅ **생태계**: 100+ LLM, 50+ 벡터 DB 지원

### **n8n을 후순위로 두는 이유**
- ⚠️ AI 로직 한계: 복잡한 체이닝은 코드가 더 나음
- ⚠️ 디버깅 어려움: GUI 기반 워크플로우
- ⚠️ 버전 관리: JSON 파일은 코드 리뷰 힘듦

**하지만 n8n의 강점:**
- ✅ 외부 SaaS 연동 (Slack, Gmail, Notion 등)
- ✅ 스케줄링 및 이벤트 트리거
- ✅ 비개발자도 사용 가능

---

## 🚀 빠른 시작

### **1단계: 환경 변수 설정**

```bash
cd my-ai-platform

# 환경 변수 파일 복사
cp env.langchain.example .env

# 비밀번호 변경 (필수!)
nano .env
```

**반드시 변경할 항목:**
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `GRAFANA_PASSWORD`

### **2단계: 인프라 서비스 시작 (기존)**

```bash
# Ollama + 모니터링 (기존 서비스)
docker compose up -d ollama prometheus grafana loki promtail
```

### **3단계: LangChain 스택 시작 (새로 추가)**

```bash
# PostgreSQL + Milvus + Redis + LangChain API
docker compose -f docker-compose.langchain.yml up -d

# 로그 확인
docker compose -f docker-compose.langchain.yml logs -f
```

### **4단계: 서비스 확인**

```bash
# 헬스 체크
curl http://localhost:8000/health

# 응답 예시:
# {
#   "status": "healthy",
#   "services": {
#     "ollama": "http://ollama:11434",
#     "postgres": "postgres:5432",
#     "milvus": "milvus:19530",
#     "redis": "redis:6379"
#   }
# }
```

---

## 📖 API 사용 예제

### **1. 기본 채팅**

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요! LangChain에 대해 설명해주세요.",
    "model": "llama2"
  }'
```

**응답:**
```json
{
  "response": "LangChain은 LLM 애플리케이션을 쉽게 개발할 수 있게 해주는...",
  "session_id": "uuid-here",
  "model": "llama2"
}
```

### **2. 문서 업로드 (RAG)**

```bash
# PDF 업로드
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@my_document.pdf"
```

**응답:**
```json
{
  "document_id": "uuid-here",
  "title": "my_document.pdf",
  "chunk_count": 42,
  "status": "completed"
}
```

### **3. RAG 검색-생성 쿼리**

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "문서에서 LangChain의 주요 기능은 무엇인가요?",
    "top_k": 5
  }'
```

**응답:**
```json
{
  "answer": "문서에 따르면 LangChain의 주요 기능은...",
  "sources": [
    {
      "content": "LangChain은 다음 기능을 제공합니다...",
      "score": 0.95,
      "metadata": {"document_id": "uuid", "chunk_index": 5}
    }
  ],
  "search_time_ms": 42,
  "generation_time_ms": 1523
}
```

### **4. LangGraph 에이전트 실행**

```bash
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "AI 보안의 최신 트렌드를 조사하고 리포트 작성",
    "agent_type": "research"
  }'
```

**응답:**
```json
{
  "result": "AI 보안의 최신 트렌드는...",
  "steps": [
    {"step": "research", "description": "정보 수집 완료", "results_count": 3},
    {"step": "analyze", "description": "분석 완료"},
    {"step": "write_report", "description": "리포트 작성 완료"},
    {"step": "review", "description": "리포트 승인"}
  ],
  "execution_time_ms": 5234,
  "status": "completed"
}
```

---

## 🛠️ 관리 대시보드

### **FastAPI 문서 (Swagger)**
- URL: http://localhost:8000/docs
- 모든 API 엔드포인트 테스트 가능

### **Milvus 관리 UI (Attu)**
- URL: http://localhost:8080
- 컬렉션, 벡터, 인덱스 관리

### **Grafana 모니터링**
- URL: http://localhost:3000
- 로그인: admin / (`.env`에서 설정한 비밀번호)

### **PostgreSQL 접속**
```bash
docker exec -it ai-postgres psql -U admin -d aiplatform

# 테이블 확인
\dt

# 대화 세션 조회
SELECT * FROM conversation_sessions LIMIT 10;
```

---

## 🔧 개발 가이드

### **로컬 개발 환경**

```bash
cd langchain_app

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
nano .env

# 개발 서버 실행
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### **디렉토리 구조**

```
langchain_app/
├── api/                    # FastAPI 애플리케이션
│   ├── main.py            # 메인 앱
│   ├── routes/            # API 라우트
│   │   ├── chat.py        # 채팅 엔드포인트
│   │   ├── rag.py         # RAG 엔드포인트
│   │   ├── documents.py   # 문서 관리
│   │   └── agents.py      # 에이전트 실행
│   └── schemas/           # Pydantic 스키마
│
├── src/                   # 핵심 LangChain 로직
│   ├── chains/            # LangChain 체인
│   │   ├── conversation.py    # 대화 체인
│   │   └── rag_chain.py       # RAG 체인
│   │
│   ├── agents/            # LangGraph 에이전트
│   │   └── research_agent.py  # 연구 에이전트
│   │
│   ├── retrievers/        # 검색기
│   │   ├── milvus_retriever.py    # Milvus 검색
│   │   └── document_processor.py  # 문서 처리
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
└── requirements.txt
```

### **새 체인 추가하기**

```python
# src/chains/my_custom_chain.py

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from src.models.llm import llm_model

class MyCustomChain:
    def __init__(self):
        self.llm = llm_model.llm
        self.prompt = PromptTemplate(...)
    
    async def run(self, input_data):
        # 로직 구현
        pass
```

### **새 에이전트 추가하기**

```python
# src/agents/my_agent.py

from langgraph.graph import StateGraph, END
from typing import TypedDict

class MyAgentState(TypedDict):
    # 상태 정의
    pass

class MyAgent:
    def _build_graph(self):
        workflow = StateGraph(MyAgentState)
        # 노드 및 엣지 추가
        return workflow.compile()
```

---

## 🔄 n8n 통합 (후순위)

n8n을 LangChain API의 **소비자**로 사용:

### **예: Slack 알림 워크플로우**

1. n8n에서 HTTP Request 노드로 LangChain API 호출
2. 결과를 받아서 Slack 메시지 전송

```
[Cron 트리거] 
  → [HTTP: POST /api/agents/execute] 
  → [Slack: 메시지 전송]
```

### **예: 문서 자동 처리**

```
[Webhook: 파일 업로드] 
  → [HTTP: POST /api/documents/upload] 
  → [조건: 성공시] 
  → [Gmail: 완료 이메일]
```

---

## 📊 모니터링

### **Grafana 대시보드 설정**

1. http://localhost:3000 접속
2. Data Sources → Prometheus, Loki 추가
3. Dashboards → Import:
   - Docker Metrics (ID: 179)
   - Loki Logs (ID: 13639)

### **LangSmith 연동 (선택사항)**

```bash
# .env에 추가
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=ai-platform

# 자동으로 모든 LangChain 호출이 LangSmith에 로깅됨
```

---

## 🐛 문제 해결

### **Milvus 연결 실패**

```bash
# etcd, minio가 먼저 시작되었는지 확인
docker compose -f docker-compose.langchain.yml ps

# 재시작
docker compose -f docker-compose.langchain.yml restart milvus
```

### **LangChain API 시작 실패**

```bash
# 로그 확인
docker compose -f docker-compose.langchain.yml logs langchain-api

# 의존성 확인
docker compose -f docker-compose.langchain.yml up -d postgres milvus redis
```

### **임베딩 속도 느림**

```python
# src/models/embeddings.py에서 GPU 활성화
model_kwargs={'device': 'cuda'}  # CPU → cuda
```

---

## 📚 참고 자료

- [LangChain 문서](https://python.langchain.com/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [Milvus 문서](https://milvus.io/docs)
- [Ollama 모델 라이브러리](https://ollama.ai/library)

---

**즐거운 AI 개발 되세요! 🎉**
