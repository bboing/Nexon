# AI Platform Architecture v2.0
## Router-based Multi-DB Search System

## 🎯 Overview

사용자 질문을 Router LLM이 분석하여 적절한 DB로 라우팅하는 지능형 검색 시스템

---

## 🏗️ System Architecture

```
User Query
    ↓
Router Agent (Query Classifier)
    ↓
┌───┴───┬─────────┬─────────┐
↓       ↓         ↓         ↓
Simple  Relation  Semantic  Complex
↓       ↓         ↓         ↓
PG      Neo4j     Milvus    Multi-DB
    ↓
Context Builder
    ↓
Answer Generator
    ↓
Final Answer
```

---

## 📊 Database Roles

### PostgreSQL (Master Data)
- **목적**: 원본 엔티티 저장 (Source of Truth)
- **데이터**: maple_dictionary 테이블
- **용도**: 정확한 정보 조회, CRUD, 필터링

### Neo4j (Relationships)
- **목적**: 엔티티 간 관계 저장
- **데이터**: 노드(Entity) + 엣지(Relationship)
- **용도**: 관계 탐색, 경로 찾기, 추천

### Milvus (Semantic Search)
- **목적**: 의미 기반 검색
- **데이터**: 텍스트 청크 + 임베딩 벡터
- **용도**: 자연어 질문 매칭, 유사도 검색

---

## 🔄 Query Types

### 1. SIMPLE_LOOKUP
- **설명**: 정확한 이름/ID로 정보 조회
- **예시**: "아이스진 가격?", "페이슨은 누구?"
- **DB**: PostgreSQL
- **평균 시간**: 0.6초

### 2. RELATIONSHIP
- **설명**: 엔티티 간 관계/경로 질문
- **예시**: "아이스진 얻으려면?", "헤네시스→커닝시티?"
- **DB**: Neo4j → PostgreSQL (상세 정보)
- **평균 시간**: 0.8초

### 3. SEMANTIC
- **설명**: 추상적/자연어 질문
- **예시**: "초보자 추천 장비", "도적 좋은 사냥터"
- **DB**: Milvus → PostgreSQL (상세 정보)
- **평균 시간**: 1.5초

### 4. COMPLEX
- **설명**: 여러 DB가 필요한 복합 질문
- **예시**: "아이스진 사고 다음엔?"
- **DB**: All (PostgreSQL + Neo4j + Milvus)
- **평균 시간**: 2.0초

---

## 📂 Implementation Structure

```
langchain_app/
├── src/
│   ├── agents/
│   │   ├── router_agent.py          # 🆕 Query 분류
│   │   └── search_agent.py          # 기존 Agent (통합)
│   ├── retrievers/
│   │   ├── db_searcher.py           # PostgreSQL
│   │   ├── neo4j_searcher.py        # 🆕 Neo4j
│   │   ├── milvus_retriever.py      # Milvus (기존)
│   │   └── hybrid_searcher.py       # 통합 (수정)
│   └── utils/
│       ├── context_builder.py       # 🆕 결과 병합
│       └── chunk_generator.py       # 🆕 Milvus 청크 생성

scripts/
├── sync_to_neo4j.py                 # 🆕 PostgreSQL → Neo4j
├── sync_to_milvus.py                # 🆕 PostgreSQL → Milvus
├── test_router.py                   # 🆕 Router 테스트
└── test_full_search.py              # 🆕 전체 시스템 테스트
```

---

## 🚀 Data Flow

### 1. Data Import (Initial Setup)
```
JSON → import_data.py → PostgreSQL
PostgreSQL → sync_to_neo4j.py → Neo4j
PostgreSQL → sync_to_milvus.py → Milvus
```

### 2. Search Flow (Runtime)
```
Query → Router → [DB Selection]
  ↓
[SIMPLE]     → PostgreSQL
[RELATION]   → Neo4j → PostgreSQL (details)
[SEMANTIC]   → Milvus → PostgreSQL (details)
[COMPLEX]    → All DBs
  ↓
Context Builder → Answer Generator → Response
```

---

## 🎯 Performance Targets

| Query Type | Target Time | DB Access | Success Rate |
|-----------|-------------|-----------|--------------|
| SIMPLE    | < 0.7초     | 1 DB      | > 95%        |
| RELATION  | < 1.0초     | 2 DBs     | > 90%        |
| SEMANTIC  | < 1.5초     | 2 DBs     | > 85%        |
| COMPLEX   | < 2.5초     | 3 DBs     | > 80%        |

---

## 📝 Development Phases

### Phase 1: Router + PostgreSQL (Current)
- [x] PostgreSQL searcher
- [x] Basic Agent
- [ ] Router Agent
- [ ] Query classification

### Phase 2: Neo4j Integration
- [ ] Neo4j schema design
- [ ] sync_to_neo4j.py
- [ ] Neo4j searcher
- [ ] Relationship queries

### Phase 3: Milvus Integration
- [ ] Chunk generation strategy
- [ ] sync_to_milvus.py
- [ ] Milvus searcher update
- [ ] Semantic search

### Phase 4: Full Integration
- [ ] Context builder
- [ ] Hybrid searcher update
- [ ] Answer generator
- [ ] End-to-end testing

---

## 🔧 Configuration

### Router LLM
- Model: llama3.1:latest
- Temperature: 0.1
- Max tokens: 500
- Purpose: Fast query classification

### Answer LLM
- Model: gemma-3-12b-it
- Temperature: 0.3
- Max tokens: 1000
- Purpose: High-quality answer generation

---

## 📊 Success Metrics

1. **Accuracy**: Router 분류 정확도 > 90%
2. **Speed**: 평균 응답 시간 < 1.5초
3. **Coverage**: 답변 가능 질문 > 95%
4. **User Satisfaction**: 사용자 만족도 측정

---

## 🔄 Maintenance

### Data Sync
```bash
# PostgreSQL 데이터 변경 후
python sync_to_neo4j.py --incremental
python sync_to_milvus.py --incremental
```

### Monitoring
- Router 분류 로그 수집
- DB별 응답 시간 모니터링
- 사용자 피드백 수집

---

## 📚 References

- LangChain Documentation
- Neo4j Cypher Guide
- Milvus Vector Database
- Router Pattern (LangChain)
