# Maple-Agent Streamlit App

Groq API 기반 하이브리드 RAG 데모 앱

## 실행 방법

### 1. 의존성 설치

```bash
# 가상환경 활성화
source ../nexon_venv/bin/activate

# ⚠️ 중요: 상위 디렉토리의 통합 requirements.txt 사용
cd ..
pip install -r requirements.txt
cd streamlit_app
```

### 2. 환경 설정

`.env` 파일이 상위 디렉토리에 있어야 합니다:

```bash
# taegyun_nexon_pj/.env
BIZ_POSTGRES_HOST=localhost
BIZ_POSTGRES_PORT=5432
BIZ_POSTGRES_DB=maple_npc_db
BIZ_POSTGRES_USER=postgres
BIZ_POSTGRES_PASSWORD=nexonJjang67!postgres

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=nexonJjang67!neo4j

MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### 3. 서비스 시작

Docker 서비스들이 실행 중이어야 합니다:

```bash
# 상위 디렉토리에서
docker-compose up -d
```

### 4. Streamlit 실행

```bash
# streamlit_app 디렉토리에서
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## Groq API Key 발급

1. [Groq Console](https://console.groq.com/) 접속
2. API Keys 메뉴에서 새 키 생성
3. Streamlit 사이드바에 입력

## 사용 가능한 모델

- `mixtral-8x7b-32768` (추천, 빠름)
- `llama-3.1-70b-versatile` (더 정확, 느림)
- `gemma2-9b-it` (가볍고 빠름)

모델은 `services/maple_rag_service.py`에서 변경 가능합니다.

## 폴더 구조

```
streamlit_app/
├── app.py                      # 메인 진입점
├── components/                 # UI 컴포넌트
│   ├── sidebar.py
│   ├── chat_interface.py
│   └── source_display.py
├── services/                   # 비즈니스 로직
│   └── maple_rag_service.py
├── .streamlit/                 # Streamlit 설정
│   ├── config.toml
│   └── secrets.toml.example
└── requirements.txt
```

## 주요 기능

- ✅ Groq API 기반 LLM
- ✅ PostgreSQL + Milvus + Neo4j 하이브리드 검색
- ✅ RRF (Reciprocal Rank Fusion) 결과 융합
- ✅ 실시간 채팅 인터페이스
- ✅ 검색 출처 및 근거 표시
- ✅ 신뢰도 점수 표시
