
# 🚀 LangChain 기반 AI Platform - 아키텍처 가이드

## 🎯 핵심 전략: LangChain 중심 + n8n 후순위

### **왜 이렇게 구성하는가?**

**LangChain 생태계 우선 (코드 기반)**
- ✅ **LangChain**: RAG, 체인, 메모리, 프롬프트 관리
- ✅ **LangGraph**: 멀티 에이전트, 복잡한 워크플로우, 상태 관리
- ✅ **Python 코드**: Git 버전 관리, pytest 테스트, 강력한 로직

**n8n 후순위 (통합 자동화)**
- ⚠️ AI 로직은 LangChain이 더 강력
- ✅ 외부 시스템 연동 (Slack, Gmail, Notion)
- ✅ 스케줄링 및 이벤트 트리거

---

## 🏗️ 레이어드 아키텍처 (개념 설계)

```
┌─────────────────────────────────────────────────────────┐
│  Layer 5: Integration & Automation (후순위)             │
│  └─ n8n (외부 시스템 연동)                             │
└─────────────────────────────────────────────────────────┘
                       ↓ webhook/API
┌─────────────────────────────────────────────────────────┐
│  Layer 4: API Gateway                                   │
│  ├─ FastAPI (LangChain/LangGraph API)                  │
│  └─ Nginx (리버스 프록시)                              │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: AI Orchestration (핵심) 🌟                   │
│  ├─ LangGraph (멀티 에이전트 워크플로우)               │
│  └─ LangChain (RAG, 체인, 메모리)                      │
└─────────────────────────────────────────────────────────┘
           ↓                           ↓
┌─────────────────────┐     ┌─────────────────────────────┐
│ Structured Data     │     │ Vector Data                 │
│ PostgreSQL (RDB)    │     │ Milvus (Vector DB)          │
│ ─────────────────── │     │ ─────────────────────────── │
│ • 사용자 정보       │     │ • 문서 임베딩               │
│ • 대화 히스토리     │     │ • 시맨틱 검색               │
│ • 메타데이터        │     │ • 유사도 검색               │
│ • 트랜잭션          │     │ • 대규모 벡터 (백만+)       │
└─────────────────────┘     └─────────────────────────────┘
           ↓                           ↓
┌─────────────────────────────────────────────────────────┐
│  Infrastructure                                         │
│  ├─ Ollama (LLM 모델 서버)                            │
│  ├─ Redis (캐싱, 세션)                                 │
│  └─ Monitoring (Prometheus, Grafana, Loki)            │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 데이터베이스 역할 분리

| 데이터 타입 | 저장소 | 이유 |
|-------------|--------|------|
| **사용자, 대화 기록** | PostgreSQL | ACID 트랜잭션, 관계형 쿼리 |
| **문서 임베딩, 벡터** | Milvus | 대규모 벡터 검색 최적화 |
| **메타데이터** | PostgreSQL | 구조화된 쿼리 (JOIN, 집계) |
| **벡터 ID 매핑** | 양쪽 | PostgreSQL에 Milvus ID 저장 |

---

## 🚀 빠른 시작

### **1단계: 환경 설정**

```bash
cd my-ai-platform

# 환경 변수 복사
cp env.langchain.example .env

# 비밀번호 변경 (필수!)
nano .env
```

### **2단계: 플랫폼 시작**

```bash
# 빠른 시작 스크립트 사용
./start-langchain.sh

# 또는 수동으로:
# 1. 기존 인프라
docker compose up -d ollama prometheus grafana

# 2. LangChain 스택
docker compose -f docker-compose.langchain.yml up -d
```

### **3단계: 확인**

```bash
# 헬스 체크
curl http://localhost:8000/health

# API 문서
open http://localhost:8000/docs

# Milvus UI
open http://localhost:8080
```

---

## 📖 주요 기능

### **1. 대화 (메모리 기반 채팅)**
- Redis 기반 세션 관리
- Ollama LLM 사용
- 대화 컨텍스트 유지

### **2. RAG (검색 증강 생성)**
- Milvus 벡터 검색
- 문서 자동 청킹 및 임베딩
- PostgreSQL 메타데이터 관리

### **3. LangGraph 에이전트**
- 멀티 스텝 워크플로우
- 조건부 분기
- 상태 기반 의사결정

### **4. n8n 통합 (선택사항)**
- LangChain API 호출
- 외부 시스템 연동
- 스케줄링

---

## 📂 프로젝트 구조

```
my-ai-platform/
├── docker-compose.yml              # 기존 인프라
├── docker-compose.langchain.yml    # LangChain 스택
├── env.langchain.example           # 환경 변수 예제
├── start-langchain.sh              # 빠른 시작 스크립트
├── LANGCHAIN_GUIDE.md              # 상세 가이드
│
├── postgres/
│   └── init.sql                    # DB 초기화
│
├── langchain_app/                  # 🌟 LangChain 애플리케이션
│   ├── api/                        # FastAPI
│   │   ├── main.py
│   │   ├── routes/                 # 엔드포인트
│   │   └── schemas/                # Pydantic 스키마
│   │
│   ├── src/                        # 핵심 로직
│   │   ├── chains/                 # LangChain 체인
│   │   ├── agents/                 # LangGraph 에이전트
│   │   ├── retrievers/             # Milvus 검색
│   │   └── models/                 # LLM, 임베딩
│   │
│   ├── config/
│   │   └── settings.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── n8n/                            # n8n (후순위)
├── ollama/                         # Ollama 모델
└── monitoring/                     # Prometheus, Grafana
```

---

## 📚 다음 단계

### **개발 순서 (권장)**

1. **LangChain 기초** (1-2주)
   - Ollama 연동
   - 간단한 RAG 파이프라인
   - 대화 메모리

2. **LangGraph 추가** (1주)
   - 멀티 에이전트
   - 조건부 워크플로우

3. **API화** (3-5일)
   - FastAPI 엔드포인트
   - 인증, 에러 핸들링

4. **n8n 통합** (선택, 2-3일)
   - HTTP 노드로 API 호출
   - 외부 시스템 연동

---

## 🔗 참고 문서

- **통합 설정 가이드**: `INTEGRATED_SETUP.md` ⭐ **NEW!**
- **LangChain 문서**: https://python.langchain.com/
- **LangGraph 문서**: https://langchain-ai.github.io/langgraph/
- **Milvus 문서**: https://milvus.io/docs
- **Langfuse 문서**: https://langfuse.com/docs

---

## 🎉 실제 구현: 3계층 아키텍처 (Integrated Setup)

### 📊 운영 계층 구조

위의 개념 설계를 기반으로, **운영 안정성을 최우선**으로 한 실제 구현이 완료되었습니다:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Application (비즈니스 로직)                   │
│  └─ LangChain API (포트 8000)                          │
│     → 2계층에 로그 전송                                  │
└─────────────────────────────────────────────────────────┘
                      ↓ logs
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Ops/Platform (모니터링/관찰성)                │
│  ├─ Langfuse Web (포트 3000) → ops-postgres 사용       │
│  ├─ Langfuse Worker (포트 3030) → ops-postgres 사용    │
│  ├─ Milvus (포트 19530, 9092) → biz-postgres 사용     │
│  └─ Attu (포트 8080)                                   │
│  → "3계층이 죽어도 살아서 로그를 봐야 함"                │
└─────────────────────────────────────────────────────────┘
                      ↓ uses
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Core Infrastructure (절대 죽으면 안 됨)       │
│  ├─ biz-postgres (5432) ← LangChain, Milvus           │
│  ├─ ops-postgres (5433) ← Langfuse (로그 폭탄 격리!)   │
│  ├─ Redis (6379, 공유)                                 │
│  ├─ Clickhouse (8123, 9000) ← Langfuse OLAP           │
│  ├─ etcd (2379) ← Milvus 메타데이터                    │
│  ├─ MinIO-Milvus (9000, 9001)                         │
│  └─ MinIO-Langfuse (9090, 9091)                       │
└─────────────────────────────────────────────────────────┘
```

### 🎯 핵심 철학: DB 분리 전략 (전략 B)

**왜 PostgreSQL을 2개로 분리했나?**

| 이슈 | 문제점 | 해결 |
|------|--------|------|
| 🔥 **로그 폭탄** | Langfuse는 LLM 호출마다 엄청난 로그를 남김 | ops-postgres로 완벽 격리 |
| 💥 **DB 장애** | 로그 DB가 죽어도 비즈니스는 계속 운영되어야 함 | 물리적 컨테이너 분리 |
| 🐌 **성능 저하** | 로그 쿼리가 비즈니스 쿼리를 느리게 만듦 | 독립적인 리소스 할당 |

**결론**: Langfuse가 더 "위쪽"이 아니라 **"기반(Base)"**입니다. LangChain 앱이 죽어도 Langfuse는 살아있어야 로그를 보며 원인을 찾을 수 있기 때문입니다.

### 🚀 빠른 시작

```bash
cd my-ai-platform

# 환경 변수 설정
cp env.integrated.example .env
nano .env  # DB 비밀번호, Langfuse 키 등 수정

# Ollama 시작 (별도)
docker compose up -d ollama

# 통합 스택 시작
docker compose -f docker-compose.integrated.yml up -d --build

# 또는 자동화 스크립트
chmod +x start-integrated.sh
./start-integrated.sh

# 상태 확인
docker compose -f docker-compose.integrated.yml ps
```

### 📋 접속 정보

| 서비스 | URL |
|--------|-----|
| LangChain API | http://localhost:8000/docs |
| Langfuse (로그) | http://localhost:3000 |
| Attu (Milvus) | http://localhost:8080 |
| MinIO-Milvus | http://localhost:9001 |
| MinIO-Langfuse | http://localhost:9090 |

### 🔧 DB 접속

```bash
# 비즈니스 DB (LangChain, Milvus)
docker exec -it ai-biz-postgres psql -U admin -d aiplatform

# Ops DB (Langfuse 로그 전용)
docker exec -it ai-ops-postgres psql -U langfuse -d langfuse
```

### 📚 상세 문서

모든 설정, 트러블슈팅, 계층별 장애 대응은 **`INTEGRATED_SETUP.md`** 참고!

---
