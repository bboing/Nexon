# Search Agent 구현 계획

## 목표
사용자 질문 → 키워드 추출 → DB 검색 → 정보 통합 → LLM 답변

## Phase 1: 핵심 컴포넌트 (1-2일)

### 1️⃣ Entity Extractor (키워드 분리) ⭐ 최우선
**목표**: "아이스진 사려면 어디로 가야 하나요?" → ["아이스진", "사다", "어디"]

**구현 방법**:
```python
# 방법 A: LLM 기반 (추천)
- Ollama LLM을 사용해 키워드 추출
- Prompt: "다음 질문에서 핵심 키워드만 추출해줘: {질문}"

# 방법 B: 규칙 기반
- 한국어 형태소 분석 (KoNLPy, Mecab)
- 명사만 추출 + 불용어 제거

# 방법 C: 하이브리드 (최선)
- 형태소 분석으로 1차 추출
- LLM으로 중요도 판단
```

**파일**: `langchain_app/src/extractors/entity_extractor.py`

---

### 2️⃣ DB Searcher (PostgreSQL 검색) ⭐ 최우선
**목표**: 추출된 키워드로 maple_dictionary 검색

**구현 방법**:
```python
# 검색 로직
1. canonical_name 정확 매칭
2. synonyms 배열 검색
3. description 키워드 검색
4. detail_data JSONB 검색 (필요시)

# PostgreSQL 쿼리 예시
SELECT * FROM maple_dictionary 
WHERE 
  canonical_name = '아이스진' OR
  '아이스진' = ANY(synonyms) OR
  description ILIKE '%아이스진%'
```

**파일**: `langchain_app/src/retrievers/db_searcher.py`

---

### 3️⃣ Context Builder (정보 병합)
**목표**: 검색 결과를 LLM이 이해할 수 있는 Context로 변환

**구현 방법**:
```python
# 예시 Context
"""
[아이템 정보]
- 이름: 아이스진
- 종류: 장비 (하의)
- 설명: 시원한 푸른색의 청바지

[판매 NPC]
- NPC 이름: 페이슨
- 위치: 리스항구
- 가격: 4800 메소
"""
```

**파일**: `langchain_app/src/builders/context_builder.py`

---

### 4️⃣ LLM Answer Generator (답변 생성)
**목표**: Context + 질문 → 자연스러운 답변

**구현 방법**:
```python
# Prompt Template
"""
당신은 메이플스토리 가이드입니다.
다음 정보를 바탕으로 사용자 질문에 답변하세요.

[정보]
{context}

[질문]
{question}

[답변 규칙]
- 친절하고 간결하게
- 정보에 없는 내용은 추측하지 말 것
- 위치나 NPC 이름은 정확히 언급
"""
```

**파일**: `langchain_app/src/generators/answer_generator.py`

---

### 5️⃣ API Endpoint (전체 연결)
**목표**: FastAPI로 전체 플로우 통합

**엔드포인트**:
```python
POST /api/search/ask
{
  "question": "아이스진 사려면 어디로 가야 하나요?"
}

→ Response:
{
  "answer": "아이스진은 리스항구에 있는 페이슨 NPC에게서 4800 메소에 구매할 수 있습니다.",
  "context": { ... },
  "keywords": ["아이스진", "사다"],
  "sources": [...]
}
```

**파일**: `langchain_app/api/routers/search.py`

---

## Phase 2: 고도화 (추후)

### 6️⃣ Graph Traverser (Neo4j 연동)
- 연관 정보 탐색 (아이템 → NPC → 위치)

### 7️⃣ Milvus Retriever (벡터 검색)
- 의미적 유사도 기반 검색
- "푸른 바지" → "아이스진" 매칭

### 8️⃣ Hybrid Ranker
- DB 검색 + 벡터 검색 결과 통합
- 점수 기반 정렬

---

## 기술 스택

### 필수
- **PostgreSQL**: maple_dictionary 검색
- **Ollama LLM**: 키워드 추출 + 답변 생성
- **SQLAlchemy**: DB ORM
- **FastAPI**: API 서버

### 선택 (Phase 2)
- **Neo4j**: 그래프 탐색
- **Milvus**: 벡터 검색
- **LangChain**: RAG 파이프라인
- **Langfuse**: 로깅/모니터링

---

## 개발 순서 (추천)

```
Day 1-2: Entity Extractor + DB Searcher
  ├─ LLM 기반 키워드 추출 구현
  └─ PostgreSQL 검색 쿼리 작성

Day 3: Context Builder + Answer Generator
  ├─ 검색 결과 → Context 변환
  └─ LLM Prompt 엔지니어링

Day 4: API Endpoint + 통합 테스트
  ├─ FastAPI 라우터 구성
  └─ 전체 플로우 테스트

Day 5+: 고도화
  ├─ Neo4j 연동 (선택)
  └─ Milvus 연동 (선택)
```

---

## 다음 단계

1. **Entity Extractor 먼저 만들까요?**
   - LLM 기반 vs 형태소 분석 vs 하이브리드

2. **아니면 DB Searcher부터?**
   - 키워드 입력 → maple_dictionary 검색

어떤 것부터 시작할까요? 🎯
