# 🪢 Langfuse 통합 가이드

## 📋 Langfuse란?

**Langfuse**는 오픈소스 LLM 관찰성(Observability) 플랫폼입니다.

### LangSmith vs Langfuse

| 특징 | Langfuse | LangSmith |
|------|----------|-----------|
| **오픈소스** | ✅ MIT 라이선스 | ❌ 클로즈드 소스 |
| **셀프 호스팅** | ✅ Docker로 가능 | ❌ 클라우드만 |
| **비용** | 무료 (셀프 호스팅) | 유료 (사용량 기반) |
| **데이터 소유권** | ✅ 완전 제어 | ⚠️ 클라우드에 저장 |
| **커스터마이징** | ✅ 소스 수정 가능 | ❌ 불가능 |
| **GitHub Stars** | 20.6k+ | N/A |

출처: [Langfuse GitHub](https://github.com/langfuse/langfuse)

---

## 🎯 주요 기능

### 1. **LLM Observability (관찰성)**
- 모든 LLM 호출 추적
- 토큰 사용량, 비용 계산
- 레이턴시 모니터링
- 에러 추적

### 2. **Prompt Management (프롬프트 관리)**
- 프롬프트 버전 관리
- A/B 테스트
- 프로덕션 배포

### 3. **Evaluation (평가)**
- 자동 평가 파이프라인
- 사용자 피드백 수집
- 품질 메트릭

### 4. **Datasets (데이터셋)**
- 테스트 데이터셋 관리
- 재현 가능한 테스트

### 5. **Playground (플레이그라운드)**
- 대화형 테스트 환경
- 다양한 모델 비교

---

## 🚀 빠른 시작

### 1단계: 환경 변수 설정

```bash
cd my-ai-platform
nano .env
```

**중요! 반드시 변경해야 할 값:**

```bash
# Langfuse 인증 (최소 32자 이상)
LANGFUSE_SECRET=2f0570813502c9cea91545af323c707386d13672d3e11e5527b57e5aae815fb9
LANGFUSE_SALT=bf1ff19198bfa0f906daf988abbddc99f8684941dafbff8a850d5336f1c1fd9e
```

**보안 키 생성 (권장):**

```bash
# 랜덤 키 생성
openssl rand -base64 32

# 또는
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2단계: Langfuse 시작

```bash
# LangChain 스택 전체 시작 (Langfuse 포함)
./start-langchain.sh

# 또는 개별 시작
docker compose -f docker-compose.langchain.yml up -d langfuse-server
```

### 3단계: Langfuse 접속 및 초기 설정

```bash
# 브라우저에서 열기
open http://localhost:3001
```

**첫 접속 시:**

1. **회원가입** 페이지가 나옵니다
2. 이메일 + 비밀번호로 계정 생성
3. 프로젝트 자동 생성됨 (기본: "ai-platform")

### 4단계: API 키 생성

1. Langfuse UI → **Settings** → **API Keys**
2. **Create New API Key** 클릭
3. **Public Key**와 **Secret Key** 복사
4. `.env` 파일에 추가:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
```

### 5단계: LangChain API 재시작

```bash
# API 컨테이너만 재시작 (환경 변수 적용)
docker compose -f docker-compose.langchain.yml restart langchain-api
```

---

## 📊 Langfuse UI 사용하기

### 대시보드 개요

접속: http://localhost:3001

#### **1. Traces (추적)**
- 모든 LLM 호출 기록
- 실행 시간, 토큰 수, 비용
- 입력/출력 내용

**예시 화면:**
```
Trace: Chat Conversation
├─ LLM Call: llama2
│  ├─ Input: "LangChain이란?"
│  ├─ Output: "LangChain은..."
│  ├─ Tokens: 150
│  └─ Duration: 2.3s
└─ Status: Success
```

#### **2. Sessions (세션)**
- 사용자별 대화 세션
- 세션별 통계

#### **3. Prompts (프롬프트)**
- 프롬프트 템플릿 관리
- 버전 관리

#### **4. Datasets (데이터셋)**
- 테스트 데이터 관리
- 평가용 데이터셋

---

## 🔍 실제 사용 예제

### 1. 채팅 추적 확인

**API 호출:**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!"}'
```

**Langfuse에서 확인:**
1. http://localhost:3001/traces 접속
2. 방금 전 호출 기록 확인
3. 클릭하면 상세 정보:
   - 입력: "안녕하세요!"
   - 출력: LLM 응답
   - 메타데이터: session_id, model, duration

### 2. RAG 파이프라인 추적

**API 호출:**
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "문서의 핵심은?"}'
```

**Langfuse에서 확인:**
```
Trace: RAG Query
├─ Retrieval: Milvus Search
│  ├─ Query: "문서의 핵심은?"
│  └─ Results: 5 documents
├─ LLM Generation
│  ├─ Context: [문서1, 문서2, ...]
│  ├─ Prompt: "다음 컨텍스트를..."
│  └─ Answer: "핵심은..."
└─ Total Duration: 3.5s
```

### 3. LangGraph 에이전트 추적

**API 호출:**
```bash
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "AI 트렌드 조사"}'
```

**Langfuse에서 확인:**
```
Trace: Research Agent
├─ Step 1: Research
│  └─ Milvus Search (42ms)
├─ Step 2: Analyze
│  └─ LLM Call (1.2s)
├─ Step 3: Write Report
│  └─ LLM Call (1.8s)
├─ Step 4: Review
│  └─ Decision: approved
└─ Total: 5.2s
```

---

## 📈 메트릭 및 분석

### 1. 토큰 사용량 추적

**Langfuse Dashboard:**
- 일별 토큰 사용량
- 모델별 비교
- 비용 추정 (Ollama는 무료이지만 API 사용 시 유용)

### 2. 성능 분석

**레이턴시 모니터링:**
- P50, P95, P99 레이턴시
- 느린 요청 식별
- 병목 지점 발견

### 3. 품질 평가

**Evaluation Metrics:**
- 사용자 피드백 (thumbs up/down)
- 자동 평가 점수
- A/B 테스트 결과

---

## 🔧 고급 기능

### 1. 커스텀 메타데이터 추가

```python
from src.models.langfuse_callback import get_langfuse_handler

# Langfuse 핸들러
handler = get_langfuse_handler()

# 커스텀 메타데이터
handler.trace(
    name="custom-operation",
    metadata={
        "user_id": "user123",
        "experiment": "version_A"
    }
)
```

### 2. 세션 그룹핑

```python
# 세션별로 그룹화
handler = get_langfuse_handler()
handler.set_session_id("session-abc-123")
```

### 3. 태그 추가

```python
# 태그로 분류
handler.add_tags(["production", "v1.0", "chatbot"])
```

---

## 🔗 통합 아키텍처

```
[사용자 요청]
      ↓
[FastAPI: /api/chat/]
      ↓
[LangChain: ConversationChain]
      ├─ callbacks=[langfuse_handler]  ← Langfuse 추적
      ↓
[Ollama LLM]
      ↓
[응답 생성]
      ↓
[Langfuse: 자동 기록]
   ├─ Input
   ├─ Output
   ├─ Tokens
   ├─ Duration
   └─ Metadata
      ↓
[Langfuse UI에서 확인]
```

---

## 🐛 문제 해결

### Langfuse 연결 실패

```bash
# Langfuse 로그 확인
docker compose -f docker-compose.langchain.yml logs langfuse-server

# 헬스 체크
curl http://localhost:3001/api/public/health
```

### API 키가 작동하지 않음

1. Langfuse UI에서 키 재생성
2. `.env` 파일 업데이트
3. LangChain API 재시작:
```bash
docker compose -f docker-compose.langchain.yml restart langchain-api
```

### 추적이 표시되지 않음

**체크리스트:**
1. ✅ `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` 설정됨?
2. ✅ LangChain API 재시작함?
3. ✅ Langfuse 서버 실행 중?

```bash
# 환경 변수 확인
docker compose -f docker-compose.langchain.yml exec langchain-api env | grep LANGFUSE
```

---

## 📊 모니터링 대시보드

### Grafana와 Langfuse 함께 사용

```
┌─────────────────────────────────────┐
│ Grafana (포트 3000)                 │
│ - 인프라 메트릭                     │
│ - 컨테이너 리소스                   │
│ - 로그 (Loki)                       │
└─────────────────────────────────────┘
                  +
┌─────────────────────────────────────┐
│ Langfuse (포트 3001)                │
│ - LLM 호출 추적                     │
│ - 토큰 사용량                       │
│ - 품질 평가                         │
└─────────────────────────────────────┘
            = 완벽한 모니터링
```

---

## 🔒 보안 권장사항

### 1. 프로덕션 환경

```bash
# .env에서 설정
LANGFUSE_SECRET=<강력한-비밀키-32자-이상>
LANGFUSE_SALT=<강력한-솔트-32자-이상>

# 텔레메트리 비활성화 (선택)
LANGFUSE_TELEMETRY=false
```

### 2. 네트워크 격리

```yaml
# docker-compose.langchain.yml
langfuse-server:
  networks:
    - ai-network  # 내부 네트워크만
  # 외부 노출 제한
```

### 3. 백업

```bash
# PostgreSQL 백업 (Langfuse 데이터 포함)
docker exec ai-postgres pg_dump -U admin aiplatform > langfuse_backup.sql
```

---

## 📚 참고 자료

- **Langfuse 공식 문서**: https://langfuse.com/docs
- **GitHub**: https://github.com/langfuse/langfuse
- **LangChain 통합**: https://langfuse.com/docs/integrations/langchain
- **API 레퍼런스**: https://api.reference.langfuse.com/

---

## 🎓 다음 단계

1. ✅ Langfuse 설치 완료
2. 🔍 첫 API 호출로 추적 테스트
3. 📊 대시보드에서 메트릭 확인
4. 🎯 프롬프트 관리 시작
5. 📈 평가 파이프라인 구축

---

**LangSmith 없이도 강력한 LLM 관찰성을 확보했습니다! 🎉**
