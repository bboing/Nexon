# 🔄 .env 파일 마이그레이션 가이드

**작업 일시**: 2026-01-28  
**목적**: Integrated 구조에 맞게 환경 변수 재구성

---

## 📊 변경 사항 요약

### **Before (기존 .env)**
- ❌ 단일 PostgreSQL
- ❌ Langfuse Cloud
- ❌ Neo4j 없음
- ❌ 하드코딩 혼재

### **After (새로운 .env)**
- ✅ 2개 PostgreSQL (Biz / Ops 분리)
- ✅ Langfuse Self-hosted (Clickhouse, MinIO)
- ✅ Neo4j 추가
- ✅ 모든 값 환경변수 참조

---

## 🗂️ 새로운 .env 구조

### **1. Layer 1: Core Infrastructure**

#### **PostgreSQL (2개로 분리)**
```bash
# 비즈니스 DB (NPC, Dictionary, Master Data)
BIZ_POSTGRES_*

# Ops DB (Langfuse 로그 전용, 격리)
OPS_POSTGRES_*
```

**이유**: 
- Langfuse 로그가 폭발적으로 증가해도 비즈니스 DB에 영향 없음
- 백업/복구 전략 분리 가능

#### **Neo4j (신규 추가)**
```bash
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

**용도**: GraphRAG의 관계 추론 (NPC-지역-보스-드랍)

#### **Redis**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0
```

**변경 없음**: 기존 값 유지

---

### **2. Layer 2: Ops/Platform**

#### **Langfuse Self-hosted (신규)**
```bash
# Web UI
LANGFUSE_PORT=3000
LANGFUSE_URL=http://localhost:3000

# 보안 키 (최소 32자 필수!)
LANGFUSE_NEXTAUTH_SECRET=...
LANGFUSE_SALT=...
LANGFUSE_ENCRYPTION_KEY=...

# Clickhouse (OLAP)
CLICKHOUSE_USER=clickhouse
CLICKHOUSE_PASSWORD=...

# MinIO (S3 Storage)
MINIO_LANGFUSE_USER=langfuse
MINIO_LANGFUSE_PASSWORD=...
```

**중요**: 
- Langfuse Cloud에서 Self-hosted로 변경
- 보안 키 생성 필요: `openssl rand -hex 32`

---

### **3. Layer 3: Application**

#### **Ollama**
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

**변경**: 
- ✅ 모델명이 환경변수로 관리됨
- ✅ docker-compose에서 직접 참조

#### **LangChain API**
```bash
LANGCHAIN_API_PORT=8000  # 기존 8001 → 8000
API_WORKERS=4
LOG_LEVEL=info
```

**변경**: 포트 8000으로 통일

---

## 🔧 docker-compose.integrated.yml 변경

### **하드코딩 제거**

#### **Before:**
```yaml
environment:
  - OLLAMA_BASE_URL=http://host.docker.internal:11434
  - MILVUS_HOST=milvus
  - REDIS_HOST=redis
  - API_HOST=0.0.0.0
```

#### **After:**
```yaml
environment:
  - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://host.docker.internal:11434}
  - MILVUS_HOST=${INTERNAL_MILVUS_HOST:-milvus}
  - REDIS_HOST=${INTERNAL_REDIS_HOST:-redis}
  - API_HOST=${LANGCHAIN_API_HOST:-0.0.0.0}
```

**장점**:
- `.env` 파일에서 중앙 관리
- 환경별로 다른 값 설정 가능
- 디폴트 값 유지 (backward compatible)

---

## 🚀 마이그레이션 단계

### **Step 1: 보안 키 생성**

```bash
# Langfuse 보안 키 생성 (3개 필요)
openssl rand -hex 32  # NEXTAUTH_SECRET
openssl rand -hex 32  # SALT
openssl rand -hex 32  # ENCRYPTION_KEY (64자)
```

### **Step 2: .env 파일 백업 (기존 값 보존)**

```bash
cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform

# 기존 .env 백업
cp .env .env.backup.$(date +%Y%m%d)
```

### **Step 3: 새 .env 확인**

이미 작성되어 있습니다:
- ✅ `/my-ai-platform/.env` (실제 사용)
- ✅ `/my-ai-platform/env.integrated.example` (템플릿)

### **Step 4: 비밀번호 수정**

`.env` 파일을 열어서 다음 값들을 **강력한 비밀번호**로 변경:

```bash
# PostgreSQL
BIZ_POSTGRES_PASSWORD=QHSRHFP67!postgres  # 이미 설정됨
OPS_POSTGRES_PASSWORD=QHSRHFP67!langfuse  # 이미 설정됨

# Neo4j
NEO4J_PASSWORD=QHSRHFP67!neo4j  # 이미 설정됨

# Redis
REDIS_PASSWORD=QHSRHFP67!redis  # 이미 설정됨

# Clickhouse
CLICKHOUSE_PASSWORD=QHSRHFP67!clickhouse  # 이미 설정됨

# MinIO
MINIO_LANGFUSE_PASSWORD=QHSRHFP67!langfuse  # 이미 설정됨

# Langfuse 보안 키 (생성 필요!)
LANGFUSE_NEXTAUTH_SECRET=your-nextauth-secret-minimum-32-characters-long-change-this
LANGFUSE_SALT=your-salt-minimum-32-characters-long-change-this-too
LANGFUSE_ENCRYPTION_KEY=0000000000000000000000000000000000000000000000000000000000000000
```

### **Step 5: Docker 재시작**

```bash
# 모든 컨테이너 중지 및 볼륨 제거 (신규 시작)
docker compose -f docker-compose.integrated.yml down -v

# 새 환경변수로 시작
docker compose -f docker-compose.integrated.yml up -d

# 로그 확인
docker compose -f docker-compose.integrated.yml logs -f
```

---

## ✅ 검증 체크리스트

### **1. 서비스 상태 확인**
```bash
./scripts/status.sh
```

**예상 결과**:
- ✅ biz-postgres (5432)
- ✅ ops-postgres (5433)
- ✅ neo4j (7474, 7687)
- ✅ milvus (19530)
- ✅ redis (6379)
- ✅ langfuse-web (3000)
- ✅ langchain-api (8000)
- ✅ open-webui (8090)

### **2. 환경변수 적용 확인**
```bash
# LangChain API 컨테이너에서 환경변수 확인
docker exec ai-langchain-api env | grep -E "POSTGRES|MILVUS|REDIS|NEO4J|OLLAMA"
```

**예상 출력**:
```
POSTGRES_HOST=biz-postgres
POSTGRES_DB=maple
MILVUS_HOST=milvus
NEO4J_HOST=neo4j
OLLAMA_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

### **3. Langfuse 초기 설정**
```bash
# 브라우저에서 접속
open http://localhost:3000

# 계정 생성 후 API 키 발급
# Settings > API Keys > Create new key
```

**중요**: 발급받은 키를 `.env`에 추가:
```bash
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
```

### **4. Neo4j 접속 확인**
```bash
open http://localhost:7474

# 로그인
# Username: neo4j
# Password: (NEO4J_PASSWORD 값)
```

---

## 🔄 롤백 (문제 발생 시)

```bash
# 1. 기존 .env 복원
cp .env.backup.YYYYMMDD .env

# 2. 컨테이너 재시작
docker compose -f docker-compose.integrated.yml down
docker compose -f docker-compose.integrated.yml up -d
```

---

## 📝 주요 차이점 정리

| 항목 | 기존 (.env.backup) | 신규 (.env) |
|------|-------------------|-------------|
| **PostgreSQL** | 1개 (POSTGRES_*) | 2개 (BIZ_*, OPS_*) |
| **Neo4j** | 없음 | 추가됨 |
| **Langfuse** | Cloud | Self-hosted |
| **API Port** | 8000 | 8000 (동일) |
| **Ollama Model** | 설정 없음 | Llama-3.1-8B-Instruct |
| **하드코딩** | docker-compose에 혼재 | 모두 .env 참조 |

---

## 🎯 다음 단계

### **필수**
1. ✅ .env 파일 생성 완료
2. ⚠️  **Langfuse 보안 키 생성 필요**
3. ⚠️  Docker 재시작 필요

### **선택사항**
- Langfuse Cloud 계속 사용하려면 `.env`에서 주석 해제
- Neo4j 비밀번호 변경
- Open WebUI 비밀번호 설정

---

**완료!** 🎉

이제 GraphRAG 아키텍처에 최적화된 환경 설정이 완료되었습니다!
