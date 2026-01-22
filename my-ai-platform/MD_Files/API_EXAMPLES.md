# 🚀 LangChain API 사용 예제

## 📌 기본 정보

- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`
- **헬스 체크**: `http://localhost:8000/health`

---

## 💬 1. 채팅 API

### 기본 채팅

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "LangChain에 대해 설명해주세요",
    "model": "llama2"
  }'
```

**응답:**
```json
{
  "response": "LangChain은 LLM 애플리케이션을...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "llama2"
}
```

### 세션 유지 (대화 컨텍스트)

```bash
# 첫 번째 메시지
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내 이름은 김철수야",
    "model": "llama2"
  }'

# 두 번째 메시지 (같은 세션)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내 이름이 뭐라고?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 대화 기록 삭제

```bash
curl -X DELETE http://localhost:8000/api/chat/550e8400-e29b-41d4-a716-446655440000
```

---

## 📄 2. 문서 관리 API

### 문서 업로드

```bash
# PDF 업로드
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/document.pdf"

# Markdown 업로드
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@README.md"

# 텍스트 파일 업로드
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@notes.txt"
```

**응답:**
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "document.pdf",
  "chunk_count": 42,
  "status": "completed"
}
```

### 문서 목록 조회

```bash
curl http://localhost:8000/api/documents/
```

### 문서 삭제

```bash
curl -X DELETE http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 🔍 3. RAG (검색-생성) API

### RAG 쿼리

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "LangChain의 주요 기능은 무엇인가요?",
    "top_k": 5
  }'
```

**응답:**
```json
{
  "answer": "문서에 따르면 LangChain의 주요 기능은...",
  "sources": [
    {
      "content": "LangChain은 다음 기능을 제공합니다: 1. 체인...",
      "score": 0.95,
      "metadata": {
        "document_id": "a1b2c3d4-e5f6-7890",
        "chunk_index": 5
      }
    },
    {
      "content": "LangChain을 사용하면 RAG를...",
      "score": 0.87,
      "metadata": {
        "document_id": "a1b2c3d4-e5f6-7890",
        "chunk_index": 12
      }
    }
  ],
  "search_time_ms": 42,
  "generation_time_ms": 1523,
  "total_time_ms": 1565
}
```

### RAG 통계

```bash
curl http://localhost:8000/api/rag/stats
```

**응답:**
```json
{
  "collection_name": "documents",
  "total_vectors": 1234,
  "dimension": 384
}
```

---

## 🤖 4. LangGraph 에이전트 API

### 연구 에이전트 실행

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
  "result": "AI 보안의 최신 트렌드는 다음과 같습니다...",
  "steps": [
    {
      "step": "research",
      "description": "정보 수집 완료",
      "results_count": 3
    },
    {
      "step": "analyze",
      "description": "분석 완료"
    },
    {
      "step": "write_report",
      "description": "리포트 작성 완료"
    },
    {
      "step": "review",
      "description": "리포트 승인"
    }
  ],
  "execution_time_ms": 5234,
  "status": "completed"
}
```

### 사용 가능한 에이전트 타입

```bash
curl http://localhost:8000/api/agents/types
```

**응답:**
```json
{
  "agents": [
    {
      "type": "research",
      "description": "정보 조사 및 분석 에이전트",
      "capabilities": ["web_search", "document_analysis", "summarization"]
    }
  ]
}
```

---

## 🐍 Python SDK 사용 예제

### 설치

```bash
pip install httpx
```

### 채팅

```python
import httpx
import asyncio

async def chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat/",
            json={
                "message": "안녕하세요!",
                "model": "llama2"
            }
        )
        print(response.json())

asyncio.run(chat())
```

### 문서 업로드 및 RAG

```python
import httpx
import asyncio

async def rag_workflow():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. 문서 업로드
        with open("document.pdf", "rb") as f:
            upload_response = await client.post(
                "http://localhost:8000/api/documents/upload",
                files={"file": f}
            )
        doc_id = upload_response.json()["document_id"]
        print(f"Document uploaded: {doc_id}")
        
        # 2. RAG 쿼리
        rag_response = await client.post(
            "http://localhost:8000/api/rag/query",
            json={
                "question": "문서의 핵심 내용은?",
                "top_k": 3
            }
        )
        print(f"Answer: {rag_response.json()['answer']}")

asyncio.run(rag_workflow())
```

### 에이전트 실행

```python
import httpx
import asyncio

async def run_agent():
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:8000/api/agents/execute",
            json={
                "task": "머신러닝 최신 트렌드 조사",
                "agent_type": "research"
            }
        )
        
        result = response.json()
        print(f"Result: {result['result']}")
        print(f"\nExecution steps:")
        for step in result['steps']:
            print(f"  - {step['step']}: {step['description']}")

asyncio.run(run_agent())
```

---

## 🧪 스트리밍 응답 (WebSocket)

### JavaScript 예제

```javascript
// WebSocket 연결 (향후 구현 예정)
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "스트리밍으로 응답해주세요",
    session_id: "my-session"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.token); // 토큰 단위로 수신
};
```

---

## 🔗 n8n 통합 예제

### HTTP Request 노드 설정

**1. 채팅 호출**
- Method: `POST`
- URL: `http://langchain-api:8000/api/chat/`
- Body (JSON):
```json
{
  "message": "{{ $json.user_input }}",
  "model": "llama2"
}
```

**2. RAG 쿼리**
- Method: `POST`
- URL: `http://langchain-api:8000/api/rag/query`
- Body (JSON):
```json
{
  "question": "{{ $json.question }}",
  "top_k": 5
}
```

**3. Slack 알림 워크플로우**
```
[Cron 트리거 (매일 9시)]
  ↓
[HTTP: POST /api/agents/execute]
  task: "어제 업로드된 문서 요약"
  ↓
[Slack: 메시지 전송]
  채널: #daily-reports
  메시지: {{ $json.result }}
```

---

## ⚡ 성능 최적화 팁

### 1. 병렬 RAG 쿼리

```python
import httpx
import asyncio

async def parallel_rag():
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post("http://localhost:8000/api/rag/query", 
                       json={"question": q})
            for q in ["질문1", "질문2", "질문3"]
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

### 2. 캐싱 (Redis 활용)

```python
# LangChain 체인에 캐싱 자동 적용됨
# 같은 쿼리는 Redis에서 즉시 반환
```

### 3. 배치 문서 업로드

```python
async def batch_upload(file_paths):
    async with httpx.AsyncClient(timeout=300.0) as client:
        tasks = []
        for path in file_paths:
            with open(path, "rb") as f:
                tasks.append(
                    client.post(
                        "http://localhost:8000/api/documents/upload",
                        files={"file": f}
                    )
                )
        return await asyncio.gather(*tasks)
```

---

## 🐛 에러 처리

### 일반적인 에러 코드

```json
// 400 Bad Request
{
  "detail": "Invalid request format"
}

// 500 Internal Server Error
{
  "detail": "Milvus connection failed"
}

// 503 Service Unavailable
{
  "detail": "Ollama service not ready"
}
```

### 재시도 로직

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def robust_query(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/rag/query",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
```

---

## 📊 모니터링

### Prometheus 메트릭

```bash
# API 호출 횟수
curl http://localhost:8000/metrics | grep api_calls_total

# 평균 응답 시간
curl http://localhost:8000/metrics | grep api_latency_seconds
```

### 로그 확인

```bash
# LangChain API 로그
docker compose -f docker-compose.langchain.yml logs -f langchain-api

# 특정 시간대 로그 (Grafana Loki)
# Grafana → Explore → Loki → {container="ai-langchain-api"}
```

---

**더 많은 예제는 `http://localhost:8000/docs`에서 확인하세요! 🎉**
