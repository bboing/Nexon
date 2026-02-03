# 🧹 아키텍처 정리 완료 보고서

**작업 일시**: 2026-01-28  
**목적**: GraphRAG 아키텍처에 불필요한 서비스 제거

---

## ❌ 삭제된 서비스

### 1️⃣ **n8n (Workflow Automation)**
- **경로**: `my-ai-platform/n8n/`
- **이유**: 비주얼 workflow 불필요, FastAPI로 직접 구현
- **영향**: 없음 (사용 안 했음)

### 2️⃣ **Prometheus + Grafana + Loki + Promtail (Monitoring Stack)**
- **경로**: 
  - `my-ai-platform/prometheus/`
  - `my-ai-platform/loki/`
  - `my-ai-platform/promtail/`
- **이유**: Langfuse가 LLM 관찰성 전담, 시스템 메트릭은 오버스펙
- **영향**: 없음 (로컬 개발 환경)

### 3️⃣ **Nginx (Reverse Proxy)**
- **경로**: `my-ai-platform/nginx/`
- **이유**: 로컬 개발 환경이므로 불필요
- **영향**: 없음 (각 서비스에 직접 접근)

### 4️⃣ **Attu (Milvus UI)**
- **위치**: `docker-compose.integrated.yml` 서비스
- **이유**: Apple Silicon 호환 문제 (exec format error)
- **영향**: 없음 (Python 스크립트로 Milvus 관리 가능)

---

## ✅ 유지된 서비스

| 레이어 | 서비스 | 포트 | 역할 |
|--------|--------|------|------|
| **Layer 1: Core Infra** | biz-postgres | 5432 | Master Storage (NPC, Dictionary) |
| | ops-postgres | 5433 | Ops DB (Langfuse 로그) |
| | neo4j | 7474, 7687 | Graph Reasoning |
| | milvus | 19530 | Semantic Search |
| | redis | 6379 | Caching |
| **Layer 2: Ops/Platform** | clickhouse | 19000, 8123 | OLAP (Langfuse) |
| | minio-langfuse | 9090, 9093 | S3 Storage (Langfuse) |
| | minio-milvus | 9000, 9001 | S3 Storage (Milvus) |
| | langfuse-worker | - | Background Jobs |
| | langfuse-web | 3000 | LLM Observability UI |
| **Layer 3: Application** | langchain-api | 8000 | NPC Chat API |
| | open-webui | 8090 | Chat UI (시연용) |

---

## 📝 수정된 파일

### 1. **docker-compose.integrated.yml**
- ✅ `attu` 서비스 제거

### 2. **env.integrated.example**
- ✅ `ATTU_PORT` 제거
- ✅ `N8N_*` 환경변수 제거
- ✅ `GRAFANA_*`, `PROMETHEUS_*`, `LOKI_*` 제거
- ✅ `NGINX_*` 제거
- ✅ `OPENWEBUI_*` 추가

### 3. **.gitignore**
- ✅ `n8n/data/` 관련 항목 제거
- ✅ `prometheus/data/`, `grafana/data/`, `loki/data/` 제거
- ✅ Node.js 섹션 정리

### 4. **scripts/status.sh**
- ✅ Attu, n8n, Prometheus, Loki 헬스체크 제거
- ✅ Neo4j 헬스체크 추가
- ✅ 디스크 사용량에서 n8n 제거
- ✅ 주요 접속 주소 업데이트

### 5. **scripts/start-integrated.sh**
- ✅ Attu 헬스체크 제거
- ✅ Neo4j 헬스체크 추가
- ✅ 주요 접속 주소 업데이트

### 6. **scripts/backup.sh**
- ✅ n8n, prometheus, loki, nginx 백업 제거
- ✅ 학습 데이터 백업 추가

### 7. **scripts/cleanup.sh**
- ✅ n8n, Grafana 관련 항목 제거
- ✅ PostgreSQL, Milvus 데이터 언급 추가
- ✅ `docker-compose.integrated.yml` 사용

---

## 🎯 최종 아키텍처

```
[User] → Open WebUI (포트: 8090)
           ↓
    LangChain API (포트: 8000)
           ↓
    ┌──────┴──────┬──────┬──────┐
    │             │      │      │
PostgreSQL     Neo4j  Milvus  Redis
(Master)      (Graph)(Vector)(Cache)
 5432/5433     7474   19530   6379
    │
    ↓ (로그)
  Langfuse
(Clickhouse + MinIO + Worker + Web)
  포트: 3000
```

---

## 🚀 다음 단계

### **Phase 1 완료 ✅**
- [x] 불필요한 서비스 제거
- [x] Neo4j 추가
- [x] NPC DB 스키마 생성
- [x] NPC Chat API 구현

### **Phase 2 구현 필요**
- [ ] Entity Extractor (용어 추출)
- [ ] Hybrid Retriever (Postgres + Milvus)
- [ ] Graph Traverser (Neo4j)
- [ ] Context Augmentation
- [ ] 세계관 데이터 파인튜닝

---

## 💡 테스트 방법

```bash
cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform

# 1. Docker 재시작
docker compose -f docker-compose.integrated.yml up -d

# 2. 상태 확인
./scripts/status.sh

# 3. NPC 데이터 import
curl -X POST http://localhost:8000/api/npc/import

# 4. NPC Chat 테스트
curl -X POST http://localhost:8000/api/npc/chat \
  -H "Content-Type: application/json" \
  -d '{"npc_name": "밍밍부인", "message": "안녕하세요?"}'
```

---

**정리 완료!** 🎉  
이제 GraphRAG 구현에 집중할 수 있습니다!
