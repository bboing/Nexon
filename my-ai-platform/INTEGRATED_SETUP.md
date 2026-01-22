# 🚀 AI Platform 통합 설정 가이드
## LangChain + Langfuse 셀프호스팅 (3계층 아키텍처)

---

## 📊 통합 아키텍처

이 통합 설정은 **3계층 아키텍처**로 구성되어 있습니다:

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

---

## 🎯 DB 분리 전략 (전략 B)

### **왜 PostgreSQL을 2개로 분리했나요?**

| 문제 | 통합 DB | 분리 DB (채택 ⭐) |
|------|---------|-------------------|
| **로그 폭탄** | ❌ Langfuse 로그가 비즈니스 DB 느려지게 함 | ✅ 완벽히 격리됨 |
| **DB 장애** | ❌ 모든 서비스 중단 | ✅ 비즈니스는 살아있음 |
| **리소스** | ✅ 메모리 절약 | ⚠️ 메모리 2배 |
| **백업** | ✅ 한 번에 | ⚠️ 2번 필요 |

**결론**: Langfuse는 LLM 호출마다 엄청난 로그를 남깁니다. 이것이 LangChain의 비즈니스 DB를 느리게 하거나 죽이는 것을 방지하기 위해 **물리적으로 컨테이너를 분리**했습니다.

---

## ⚠️ 포트 충돌 주의

기존 `docker-compose.yml`과 포트 충돌이 발생할 수 있습니다:

| 서비스 | 기존 포트 | 통합 포트 | 충돌 |
|--------|-----------|-----------|------|
| Grafana | 3000 | - | ❌ Langfuse와 충돌! |
| PostgreSQL | 5432 | 5432 (biz) + 5433 (ops) | ✅ 분리됨 |
| Redis | 6379 | 6379 | ✅ 공유 |

**해결책**: 기존 `docker-compose.yml`의 Grafana 포트를 변경하거나, 통합 스택만 실행하세요.

---

## 🚀 빠른 시작

### **1단계: 환경 변수 설정**

```bash
cd my-ai-platform

# 환경 변수 복사
cp env.integrated.example .env

# 필수 변경 사항
nano .env
```

**반드시 변경해야 할 값:**

```bash
# 비즈니스 DB (LangChain, Milvus용)
BIZ_POSTGRES_PASSWORD=your_secure_password_here

# Ops DB (Langfuse용, 로그 격리!)
OPS_POSTGRES_PASSWORD=your_langfuse_db_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# Clickhouse
CLICKHOUSE_PASSWORD=your_clickhouse_password_here

# Langfuse 보안 키 (최소 32자!)
LANGFUSE_NEXTAUTH_SECRET=$(openssl rand -hex 32)
LANGFUSE_SALT=$(openssl rand -hex 32)
LANGFUSE_ENCRYPTION_KEY=$(openssl rand -hex 32)

# MinIO
MINIO_LANGFUSE_PASSWORD=langfusesecret_changeme
MINIO_MILVUS_PASSWORD=minioadmin_changeme
```

### **2단계: Ollama 시작** (별도)

통합 스택에는 Ollama가 포함되지 않았습니다. 별도로 시작하세요:

```bash
# 방법 1: 기존 docker-compose.yml 사용
docker compose up -d ollama

# 방법 2: 직접 설치
# https://ollama.ai 참고
```

### **3단계: 통합 스택 시작**

```bash
# 캐시 없이 빌드 및 시작
docker compose -f docker-compose.integrated.yml up -d --build

# 로그 확인
docker compose -f docker-compose.integrated.yml logs -f
```

또는 **자동화 스크립트** 사용:

```bash
chmod +x start-integrated.sh
./start-integrated.sh
```

### **4단계: 초기화 대기**

```bash
# 상태 확인 (모든 서비스가 healthy 될 때까지 대기)
docker compose -f docker-compose.integrated.yml ps

# 예상 시간: 2-3분
```

---

## 📋 서비스 접속

### **주요 서비스**

| 서비스 | URL | 용도 |
|--------|-----|------|
| **LangChain API** | http://localhost:8000/docs | API 문서 |
| **Langfuse Web** | http://localhost:3000 | LLM 관찰성 UI |
| **Attu** | http://localhost:8080 | Milvus 관리 |
| **MinIO-Milvus** | http://localhost:9001 | 객체 스토리지 (Milvus) |
| **MinIO-Langfuse** | http://localhost:9090 | 객체 스토리지 (Langfuse) |

### **데이터베이스 접속**

```bash
# 비즈니스 PostgreSQL
docker exec -it ai-biz-postgres psql -U admin -d aiplatform

# Ops PostgreSQL (Langfuse)
docker exec -it ai-ops-postgres psql -U langfuse -d langfuse

# Redis
docker exec -it ai-redis redis-cli -a changeme

# Clickhouse
docker exec -it ai-clickhouse clickhouse-client --user clickhouse --password clickhouse
```

---

## 🔧 Langfuse 초기 설정

### **1. Langfuse UI 접속**

```bash
open http://localhost:3000
```

### **2. 계정 생성**

- 이메일 + 비밀번호로 회원가입
- 프로젝트 자동 생성

### **3. API 키 생성**

1. **Settings** → **API Keys**
2. **Create New API Key**
3. Public Key (`pk-lf-xxx`)와 Secret Key (`sk-lf-xxx`) 복사

### **4. 환경 변수 업데이트**

```bash
nano .env
```

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
```

### **5. LangChain API 재시작**

```bash
docker compose -f docker-compose.integrated.yml restart langchain-api
```

---

## 🧪 테스트

### **1. LangChain API 테스트**

```bash
# 헬스 체크
curl http://localhost:8000/health

# 채팅 테스트
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!"}'
```

### **2. Langfuse 추적 확인**

```bash
# 브라우저에서
open http://localhost:3000/traces
```

방금 전 채팅 기록이 Langfuse에 표시되어야 합니다.

### **3. Milvus 연결 테스트**

```bash
# 문서 업로드 (RAG 테스트)
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.pdf"
```

### **4. DB 분리 확인**

```bash
# 비즈니스 DB 테이블
docker exec -it ai-biz-postgres psql -U admin -d aiplatform -c "\dt"

# Ops DB 테이블 (Langfuse)
docker exec -it ai-ops-postgres psql -U langfuse -d langfuse -c "\dt"
```

---

## 📊 리소스 요구사항

### **최소 사양**

- **CPU**: 4 코어
- **메모리**: 16GB (DB 2개로 분리 시 필수!)
- **디스크**: 50GB

### **권장 사양**

- **CPU**: 8 코어
- **메모리**: 32GB
- **디스크**: 100GB

### **예상 리소스 사용량**

| 서비스 | 메모리 | 디스크 |
|--------|--------|--------|
| **Layer 1** | | |
| biz-postgres | 512MB | 5GB |
| ops-postgres | 512MB | 10GB (로그 많음!) |
| Redis | 256MB | 1GB |
| Clickhouse | 2GB | 10GB |
| etcd | 128MB | 1GB |
| MinIO (2개) | 512MB | 10GB |
| **Layer 2/3** | | |
| Milvus | 2GB | 10GB |
| LangChain API | 1GB | 2GB |
| Langfuse (2개) | 1GB | 5GB |
| **총합** | **~9GB** | **~54GB** |

---

## 🔄 업그레이드

### **Langfuse 업그레이드**

```bash
# 최신 이미지 다운로드
docker compose -f docker-compose.integrated.yml pull langfuse-web langfuse-worker

# 재시작
docker compose -f docker-compose.integrated.yml up -d langfuse-web langfuse-worker
```

### **LangChain 애플리케이션 업그레이드**

```bash
# 재빌드
docker compose -f docker-compose.integrated.yml build --no-cache langchain-api

# 재시작
docker compose -f docker-compose.integrated.yml up -d langchain-api
```

---

## 🛑 중지 및 정리

### **서비스 중지**

```bash
# 모든 컨테이너 중지
docker compose -f docker-compose.integrated.yml down
```

### **데이터 포함 완전 삭제**

```bash
# 볼륨까지 삭제 (주의!)
docker compose -f docker-compose.integrated.yml down -v
```

### **개별 서비스 재시작**

```bash
# Langfuse만 재시작
docker compose -f docker-compose.integrated.yml restart langfuse-web langfuse-worker

# LangChain API만 재시작
docker compose -f docker-compose.integrated.yml restart langchain-api
```

---

## 🐛 문제 해결

### **1. 서비스가 시작되지 않음**

```bash
# 로그 확인
docker compose -f docker-compose.integrated.yml logs [service-name]

# 예: Langfuse 로그
docker compose -f docker-compose.integrated.yml logs langfuse-web
```

### **2. 포트 충돌**

```bash
# 사용 중인 포트 확인
netstat -tuln | grep -E "3000|5432|5433|6379|8000|9000"

# 충돌하는 기존 컨테이너 중지
docker compose down
```

### **3. Clickhouse 연결 실패**

```bash
# Clickhouse 로그 확인
docker compose -f docker-compose.integrated.yml logs clickhouse

# 재시작
docker compose -f docker-compose.integrated.yml restart clickhouse

# 1분 대기 후 Langfuse 재시작
docker compose -f docker-compose.integrated.yml restart langfuse-web langfuse-worker
```

### **4. MinIO 버킷 누락**

```bash
# MinIO 로그 확인
docker compose -f docker-compose.integrated.yml logs minio-langfuse

# 수동으로 버킷 생성
docker exec -it ai-minio-langfuse sh
mc alias set local http://localhost:9000 langfuse langfusesecret
mc mb local/langfuse
```

### **5. ops-postgres 연결 실패 (Langfuse)**

```bash
# Langfuse가 biz-postgres에 연결하려고 하면 실패합니다!
# .env 확인
cat .env | grep OPS_POSTGRES

# 환경 변수가 없으면 docker-compose는 기본값 사용
# 재시작
docker compose -f docker-compose.integrated.yml restart langfuse-web langfuse-worker
```

### **6. 메모리 부족**

```bash
# 리소스 사용량 확인
docker stats

# Docker Desktop 메모리 증가
# Settings → Resources → Memory: 16GB 이상
```

---

## 🎓 계층별 장애 대응

### **Layer 1 장애 (Core Infra)**

```bash
# biz-postgres 죽음 → LangChain, Milvus 중단 (치명적!)
docker compose -f docker-compose.integrated.yml restart biz-postgres

# ops-postgres 죽음 → Langfuse만 중단 (비즈니스는 계속 운영)
docker compose -f docker-compose.integrated.yml restart ops-postgres
```

### **Layer 2 장애 (Ops/Platform)**

```bash
# Langfuse 죽음 → 로그만 안 남음, LangChain은 정상
docker compose -f docker-compose.integrated.yml restart langfuse-web langfuse-worker

# Milvus 죽음 → RAG 불가, 채팅은 가능
docker compose -f docker-compose.integrated.yml restart milvus
```

### **Layer 3 장애 (Application)**

```bash
# LangChain API 죽음 → 비즈니스 중단
docker compose -f docker-compose.integrated.yml restart langchain-api
```

---

## 📚 참고 자료

- **LangChain 문서**: https://python.langchain.com/
- **Langfuse 문서**: https://langfuse.com/docs
- **Milvus 문서**: https://milvus.io/docs
- **Clickhouse 문서**: https://clickhouse.com/docs

---

## 🎯 다음 단계

1. ✅ 통합 스택 시작
2. ✅ Langfuse API 키 생성
3. 📊 첫 번째 LLM 호출 추적
4. 🔍 Milvus에 문서 업로드
5. 📈 Langfuse 대시보드에서 메트릭 확인
6. 🔥 부하 테스트로 DB 분리의 효과 확인!

---

**3계층 아키텍처로 강력하고 안정적인 AI 플랫폼이 완성되었습니다! 🎉**
