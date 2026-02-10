# Nexon Maple-Agent Platform

하이브리드 RAG 기반 메이플스토리 지식 베이스 플랫폼

## 프로젝트 구조

```
taegyun_nexon_pj/
├── requirements.txt              # 🔥 통합 의존성 (여기서 설치!)
├── docker-compose.yml            # 인프라 정의
├── .env                          # 환경 변수
│
├── langchain_app/                # RAG 엔진 (코어 로직)
│   ├── src/
│   │   ├── agents/               # Router Agent
│   │   ├── retrievers/           # Hybrid Searcher (PG+Milvus+Neo4j)
│   │   └── generators/           # Answer Generator
│   ├── database/                 # DB 연결 & 모델
│   └── config/                   # 설정
│
├── streamlit_app/                # 데모 웹 앱 (Groq API)
│   ├── app.py                    # 메인 진입점
│   ├── components/               # UI 컴포넌트
│   └── services/                 # RAG 서비스 래퍼
│
├── scripts/                      # 유틸리티 스크립트
│   ├── setup.sh                  # 초기화 스크립트
│   ├── import_data.py            # 데이터 import
│   ├── sync_to_milvus.py         # Milvus 동기화
│   └── sync_to_neo4j.py          # Neo4j 동기화
│
└── training/data/                # 학습 데이터
    └── input_data/
        └── maple_data.json       # 메이플 지식 베이스
```

## 빠른 시작

### 1. 의존성 설치

```bash
# 가상환경 생성 및 활성화
python3 -m venv nexon_venv
source nexon_venv/bin/activate

# 🔥 통합 의존성 설치 (최상위 requirements.txt)
pip install -r requirements.txt
```

### 2. 인프라 시작

```bash
# Docker 서비스 시작 (PostgreSQL, Milvus, Neo4j, Redis 등)
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 3. 데이터베이스 초기화

```bash
# 자동 초기화 스크립트 실행
bash scripts/setup.sh
```

이 스크립트는:
- PostgreSQL에 데이터 import
- Milvus에 벡터 동기화
- Neo4j에 관계 그래프 구축

### 4-A. Streamlit 데모 실행 (Groq API)

```bash
cd streamlit_app
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

**Groq API Key 발급**: https://console.groq.com/

### 4-B. FastAPI 서버 실행 (Ollama)

```bash
cd langchain_app
uvicorn main:app --reload --port 8000
```

API 문서: `http://localhost:8000/docs`

## 의존성 관리 ⚠️

이 프로젝트는 **통합 requirements.txt**를 사용합니다:

```
taegyun_nexon_pj/
├── requirements.txt              # 🔥 메인 (모든 의존성 포함)
├── langchain_app/
│   ├── requirements.txt          # ⚠️ 참고용 (사용 금지)
│   └── Dockerfile                # ← 통합 requirements.txt 사용
├── streamlit_app/
│   └── requirements.txt          # ⚠️ 참고용 (사용 금지)
└── scripts/
    ├── requirements.txt          # ⚠️ 참고용 (사용 금지)
    └── setup.sh                  # ← 통합 requirements.txt 사용
```

### 로컬 개발
```bash
# ✅ 올바른 방법
pip install -r requirements.txt

# ❌ 잘못된 방법 (버전 충돌 발생)
# pip install -r langchain_app/requirements.txt
# pip install -r streamlit_app/requirements.txt
# pip install -r scripts/requirements.txt
```

### Docker 빌드
Dockerfile도 자동으로 통합 requirements.txt를 사용합니다:
```dockerfile
# langchain_app/Dockerfile
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
```

### 자동화 스크립트
`scripts/setup.sh`도 통합 버전 사용:
```bash
pip install -r "${ROOT_DIR}/requirements.txt"
```

## 주요 기능

### 하이브리드 RAG 엔진
- **PostgreSQL**: 정확한 키워드 매칭 (이름, 카테고리)
- **Milvus**: 의미 기반 벡터 검색 (유사도)
- **Neo4j**: 그래프 관계 추론 (NPC↔MAP, MONSTER↔ITEM)
- **RRF**: Reciprocal Rank Fusion으로 결과 융합

### Router Agent
- LLM 기반 쿼리 의도 분석
- Multi-step 검색 전략 수립
- SQL_DB, GRAPH_DB, VECTOR_DB 조합

### Answer Generator
- Groq/Ollama LLM으로 자연어 답변 생성
- 검색 출처 추적
- 신뢰도 점수 계산 (60% 이하 시 안전 응답)

## 환경 변수 (.env)

```bash
# PostgreSQL
BIZ_POSTGRES_HOST=localhost
BIZ_POSTGRES_PORT=5432
BIZ_POSTGRES_DB=maple_npc_db
BIZ_POSTGRES_USER=postgres
BIZ_POSTGRES_PASSWORD=nexonJjang67!postgres

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=nexonJjang67!neo4j

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Ollama (로컬 LLM)
OLLAMA_BASE_URL=http://localhost:11434
```

## 테스트 질문 예시

- "도적 전직 어디서?"
- "스포아 어디서 잡아?"
- "아이스진 구하는 방법"
- "커닝시티에 어떤 NPC 있어?"
- "리스항구 가는 법"

## 기술 스택

### Backend
- **LangChain**: RAG 오케스트레이션
- **FastAPI**: REST API
- **SQLAlchemy**: ORM

### Database
- **PostgreSQL**: 메인 데이터 저장소
- **Milvus**: 벡터 DB (임베딩)
- **Neo4j**: 그래프 DB (관계)
- **Redis**: 캐시

### LLM
- **Ollama**: 로컬 LLM (gemma-3-12b)
- **Groq API**: 클라우드 LLM (mixtral-8x7b)

### Frontend
- **Streamlit**: 데모 웹 앱

### Monitoring
- **Langfuse**: LLM 추적 및 분석

## 라이센스

MIT License

## 문의

포트폴리오 프로젝트 - Nexon R&D 게임 NPC 대화 시스템
