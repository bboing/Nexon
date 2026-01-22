# 📝 Changelog

All notable changes to this AI Platform project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### 📋 포트폴리오 문서 최신화 - 2026-01-21

#### Changed
- 🔧 **`NEXON_PORTFOLIO_PLAN.md`** - 실제 구현 상태 반영
  - Phase 3 (파인튜닝 경험) 완료 상태로 업데이트
  - Unsloth → Apple MLX로 변경
  - 실제 파일 경로 및 구조 반영 (training/, scripts/)
  - 실제 데이터셋 정보 추가 (메이플스토리 NPC 50개)
  - 면접 답변 예시를 실제 구현 기반으로 수정
  - 프로젝트 구조 및 실행 방법 업데이트
  - 완료된 항목 체크 (✅) 및 차별점 강조

### 🔧 GGUF 변환 스크립트 개선 - 2026-01-21

#### Changed
- 🔧 **`training/scripts/convert_to_gguf.py`** - 디렉토리 자동 생성
  - `mkdir(parents=True, exist_ok=True)` 추가
  - 출력 디렉토리 없을 때 자동 생성
  - 에러 방지 및 안정성 향상

### 📚 MLX 완전 가이드 업데이트 - 2026-01-19 (Update 2)

#### Changed
- 🔧 **`MLX_FINETUNING_COMPLETE_GUIDE.md`** - 용어 및 설명 대폭 개선
  - **용어 사전 섹션 추가**: Loss, Iteration, Batch Size, Learning Rate, LoRA 파라미터 등 기본 개념을 실생활 비유와 함께 쉽게 설명
  - **인자(Arguments) 섹션 개선**: 각 인자별로 실생활 비유, 표, 다이어그램 추가
  - **상황별 추천 설정**: 빠른 테스트(10분), 기본 학습(30분), 실전 학습(2시간), 최고 품질(5시간+)
  - **트러블슈팅 확장**: 메모리 부족, Loss 발산, 과적합 등 실제 문제 상황과 해결 방법
  - 초보자도 이해 가능한 수준으로 설명 강화

### 📚 MLX 완전 가이드 추가 - 2026-01-19

#### Added
- ✨ **`MLX_FINETUNING_COMPLETE_GUIDE.md`** - MLX 파인튜닝 완전 정리 문서
  - 전체 프로세스 개요 (단계별 흐름도)
  - 핵심 개념 이해 (LoRA, Ollama vs MLX)
  - 파일 구조 설명
  - 실행 과정 상세 설명
  - 모든 인자(Arguments) 완전 정리
  - 실제 실행 로그 분석
  - 결과물 이해 및 사용 방법
  - 트러블슈팅 가이드
  - 체크리스트

### 🍎 Apple MLX 환경 추가 - 2026-01-19

#### Added
- ✨ **Apple MLX 파인튜닝 환경 구축**
  - `training/mlx-env/` - MLX 전용 Python 가상환경
  - `training/scripts/finetune_mlx.py` - MLX LoRA 파인튜닝 스크립트
  - `scripts/start-mlx-training.sh` - MLX 학습 자동화 스크립트
  - `training/MLX_GUIDE.md` - MLX 사용 가이드
  - Apple Silicon (M1/M2/M3) Metal GPU 가속 지원
  - 로컬 환경에서 5~10분 내 빠른 파인튜닝 가능

#### Changed
- 🔧 **`training/README.md`** - MLX 전용으로 업데이트
  - Unsloth/Jupyter 관련 내용 제거
  - MLX 사용법 및 데이터 형식 추가

#### Removed
- 🗑️ **Unsloth/LoRA 관련 파일 정리**
  - `docker-compose.training.yml` (GPU 기반 Unsloth)
  - `docker-compose.training-cpu.yml` (CPU 기반 LoRA)
  - `env.training.example`
  - `training/scripts/finetune_example.py` (Unsloth 예시)
  - `training/scripts/finetune_cpu.py` (일반 LoRA)
  - `scripts/start-training.sh` (Docker 기반)
  - MLX 사용으로 Docker 불필요, 로컬 환경에서 직접 실행

### 🐛 Bug Fix - 2026-01-16 (Update 2)

#### Fixed
- 🐛 **langchain_app/requirements.txt 버전 오류 수정**
  - `langfuse>=3.146.0` → `langfuse>=3.0.0` (존재하지 않는 버전 수정)
  - PyPI의 실제 최신 버전: 3.12.0
  - Docker 이미지 버전(3.x)과 Python SDK 버전을 혼동한 문제

### 🎯 Major Architecture Update - 2026-01-16

#### Added
- ✨ **3계층 아키텍처 구현** (Layer 1: Core Infra / Layer 2: Ops/Platform / Layer 3: Application)
- 📦 **`docker-compose.integrated.yml`** - 모든 서비스를 통합한 단일 Docker Compose 파일
  - PostgreSQL 2개로 분리 (biz-postgres 5432, ops-postgres 5433)
  - Langfuse v3 셀프호스팅 (Web + Worker)
  - Clickhouse for Langfuse OLAP
  - MinIO 2개로 분리 (Milvus용, Langfuse용)
  - Redis, etcd 통합
- 📄 **`env.integrated.example`** - 통합 환경변수 예제 파일
- 📖 **`INTEGRATED_SETUP.md`** - 통합 설정 가이드 문서
  - 3계층 아키텍처 다이어그램
  - DB 분리 전략 (전략 B) 설명
  - 계층별 장애 대응 가이드
  - 포트 맵핑 전체 정리
- 🚀 **`start-integrated.sh`** - 통합 스택 시작 스크립트

#### Changed
- 🔧 **PostgreSQL 분리 전략 적용**
  - `biz-postgres` (5432): LangChain, Milvus용 비즈니스 DB
  - `ops-postgres` (5433): Langfuse 전용 로그 DB (로그 폭탄 격리)
- 🔧 **포트 충돌 해결**
  - Clickhouse Native: `127.0.0.1:19000:9000` (MinIO-Milvus 9000과 충돌 방지)
  - MinIO-Langfuse Console: `127.0.0.1:9093:9001` (ai-milvus 9091과 충돌 방지)
  - Milvus Metric: `9092:9091` (외부 포트 9092로 변경)
- 🔧 **Docker 네트워크 설정 수정**
  - `external: true` → `driver: bridge` (네트워크 자동 생성)
  - 모든 서비스를 단일 `ai-network`로 통합
- 🔧 **Langfuse 컨테이너 간 통신 수정**
  - Clickhouse URL: `clickhouse://clickhouse:9000` (19000 → 9000, 내부 포트 사용)
  - MinIO Endpoint: `http://minio-langfuse:9000` (localhost:9090 → Docker DNS 사용)
- 📝 **READMEPJ.md 업데이트**
  - 실제 구현된 3계층 아키텍처 섹션 추가
  - 개념 설계 vs 실제 구현 비교
  - DB 분리 전략 철학 설명

#### Removed
- 🗑️ **통합으로 인해 불필요해진 파일들 삭제**
  - `docker-compose.langchain.yml` → `docker-compose.integrated.yml`로 통합
  - `docker-compose.override.yml` → 필요없음
  - `env.langchain.example` → `env.integrated.example`로 통합
  - `start-langchain.sh` → `start-integrated.sh`로 대체
  - `scripts/start-all.sh` → 직접 docker-compose 사용 권장
  - `scripts/start-core.sh` → 통합 파일로 불필요
  - `scripts/start-monitoring.sh` → 통합 파일로 불필요
  - `scripts/start-workflow.sh` → 통합 파일로 불필요

#### Fixed
- 🐛 **Clickhouse 연결 실패 수정**
  - 포트 매핑: `19000:19000` → `19000:9000` (컨테이너 내부 포트 수정)
  - 연결 URL: Docker 네트워크 내부 포트 9000 사용
- 🐛 **Langfuse MinIO 연결 실패 수정**
  - `localhost:9090` → `minio-langfuse:9000` (Docker DNS 사용)
  - 컨테이너 간 통신 시 Docker 네트워크 내부 이름 사용
- 🐛 **네트워크 "not found" 에러 수정**
  - `external: true` 제거, Docker Compose가 자동 생성하도록 변경

---

## 📋 Migration Guide

### 기존 설정에서 마이그레이션

#### 1. 기존 컨테이너 중지

```bash
cd my-ai-platform
docker compose down
```

#### 2. 환경 변수 업데이트

```bash
# 새로운 통합 환경변수 파일 사용
cp env.integrated.example .env

# DB 분리 설정 추가
nano .env
# BIZ_POSTGRES_* : 비즈니스 DB
# OPS_POSTGRES_* : Ops DB (Langfuse)
```

#### 3. 통합 스택 시작

```bash
# Ollama 먼저 (별도)
docker compose up -d ollama

# 통합 스택
docker compose -f docker-compose.integrated.yml up -d --build
```

#### 4. 데이터 마이그레이션 (필요시)

기존 PostgreSQL 데이터를 새로운 분리 DB로 마이그레이션:

```bash
# 기존 데이터 백업
docker exec ai-postgres pg_dump -U admin aiplatform > backup.sql

# 새 biz-postgres로 복원
docker exec -i ai-biz-postgres psql -U admin aiplatform < backup.sql
```

---

## 🎯 Breaking Changes

### 포트 변경

| 서비스 | 이전 | 현재 | 이유 |
|--------|-----|------|------|
| ops-postgres | - | 5433 | 새로 추가 (Langfuse 전용) |
| Clickhouse Native | 9000 | 127.0.0.1:19000 | MinIO 충돌 방지 |
| MinIO-Langfuse Console | - | 127.0.0.1:9093 | Milvus 9091 충돌 방지 |
| Milvus Metric | 9091 | 9092 | 외부 포트 변경 |

### 환경 변수 변경

```bash
# 이전
POSTGRES_DB=aiplatform
POSTGRES_USER=admin
POSTGRES_PASSWORD=changeme
POSTGRES_PORT=5432

# 현재 (분리됨)
BIZ_POSTGRES_DB=aiplatform        # 비즈니스 DB
BIZ_POSTGRES_USER=admin
BIZ_POSTGRES_PASSWORD=changeme
BIZ_POSTGRES_PORT=5432

OPS_POSTGRES_DB=langfuse           # Ops DB
OPS_POSTGRES_USER=langfuse
OPS_POSTGRES_PASSWORD=changeme
OPS_POSTGRES_PORT=5433
```

---

## 📚 Documentation Updates

- 📖 **INTEGRATED_SETUP.md**: 통합 설정 전체 가이드
- 📖 **READMEPJ.md**: 3계층 아키텍처 실제 구현 추가
- 📖 **CHANGELOG.md**: 이 파일 (변경 이력)

---

## 🚀 Next Steps

- [ ] 통합 스택 부하 테스트
- [ ] DB 분리의 실제 성능 효과 측정
- [ ] Grafana 대시보드 재구성 (분리된 DB 모니터링)
- [ ] CI/CD 파이프라인 업데이트
- [ ] 백업 스크립트 업데이트 (2개 DB 대응)

---

## 🙏 Acknowledgments

- **DB 분리 전략**: Langfuse 로그 폭탄으로부터 비즈니스 DB 격리
- **3계층 철학**: "Langfuse가 더 '위쪽'이 아니라 '기반(Base)'"
- **단순화**: 여러 docker-compose 파일 → 하나의 통합 파일

---

**마지막 업데이트**: 2026-01-16  
**메인테이너**: @taegyunkim
