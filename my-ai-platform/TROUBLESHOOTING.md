# 🔧 Troubleshooting & Solutions

이 문서는 개발 중 겪었던 주요 문제와 해결 방법을 기록합니다.

---

## 📋 목차

1. [Docker 환경 설정](#1-docker-환경-설정)
2. [데이터 정규화](#2-데이터-정규화)
3. [Milvus 검색 개선](#3-milvus-검색-개선)
4. [Intent 분석 (Router Agent)](#4-intent-분석-router-agent)

---

## 1. Docker 환경 설정

### 문제 1-1: Python 의존성 관리
**증상**: `sentence-transformers` 같은 패키지가 Docker에서만 필요한데, 로컬과 Docker 의존성이 분리되지 않음

**해결**:
```bash
# 구조 분리
langchain_app/requirements.txt  # FastAPI 서비스용
scripts/requirements.txt         # 유틸리티 스크립트용
```

### 문제 1-2: 스크립트가 Docker 내부에서 실행 안됨
**증상**: `scripts/` 폴더가 Docker 컨테이너에 마운트되지 않음

**해결**:
```yaml
# docker-compose.integrated.yml
langchain-api:
  build:
    context: .              # 프로젝트 root
    dockerfile: ./langchain_app/Dockerfile
  volumes:
    - ./langchain_app:/app/langchain_app
    - ./scripts:/app/scripts  # 추가!
```

### 문제 1-3: 환경변수가 `docker exec`에서 안 먹힘
**증상**: Docker Compose의 `environment`가 `docker exec bash` 세션에 적용 안됨

**해결**:
```dockerfile
# Dockerfile에 ENV 직접 설정
ENV BIZ_POSTGRES_HOST=biz-postgres
ENV MILVUS_HOST=milvus
ENV REDIS_HOST=redis
```

### 문제 1-4: PostgreSQL 연결 실패 (localhost)
**증상**: Container 내부에서 `localhost`로 PostgreSQL 접속 시도 → 연결 거부

**해결**:
```python
# Docker 네트워크 내에서는 service name 사용
host = "biz-postgres"  # not "localhost"
```

---

## 2. 데이터 정규화

### 문제 2-1: 같은 Category 내 데이터 구조 불일치
**증상**: 같은 Category(MAP, ITEM, NPC, MONSTER)인데 detail_data 필드가 중구난방

**해결**:
```bash
# 정규화 스크립트 실행
python scripts/normalize_maple_data.py
```

**핵심 로직**:
```python
# Category별 표준 스키마 정의
STANDARD_SCHEMAS = {
    "MAP": {
        "star_force_limit": 0,  # None 대신 기본값
        "arcane_power_limit": 0,
        ...
    }
}

# None 값 → 기본값 처리
if key in detail_data and detail_data[key] is not None:
    normalized[key] = detail_data[key]
else:
    normalized[key] = default_value  # 기본값 사용
```

### 문제 2-2: Pydantic 검증 실패
**증상**: `None` 값이 `int` 필드에 들어가서 validation error

**해결**:
- 정규화 시 `None` 대신 타입에 맞는 기본값 사용
- `int` → `0`, `list` → `[]`, `enum` → 기본 enum 값

---

## 3. Milvus 검색 개선

### 문제 3-1: Q&A 답변이 불완전
**증상**: "리스항구은(는) 빅토리아 아일랜드의 첫 관문" ← 문장 끝남

**원인**: 짧은 `description` 필드 사용

**해결**:
```python
# qa_generator.py
# detail_data.description 우선 사용 (더 자세함)
description = detail.get('description') or entity.get('description', '')
```

### 문제 3-2: MilvusRetriever API 불일치
**증상**: `search(query_text=...)` 메서드 없음

**해결**:
```python
# LangChain Retriever 호환
def get_relevant_documents(self, query: str) -> List[Dict]:
    return self.search(query, top_k=5)
```

### 문제 3-3: Milvus 컬렉션 불일치
**증상**: `documents` 컬렉션 찾는데, 실제로는 `maple_qa` 컬렉션 사용

**해결**:
```python
# MilvusRetriever 기본 컬렉션 변경
def __init__(self, collection_name: str = None):
    self.collection_name = collection_name or "maple_qa"
```

---

## 4. Intent 분석 (Router Agent)

### 문제 4-1: "도적 사냥터"와 "도적 전직" 구분 실패
**증상**:
- "도적 사냥터 추천" → 여섯갈래길(MAP) 높은 점수 ❌
- "도적 전직 어디서?" → 다크로드(NPC) 낮은 점수 ❌

**원인**: 단순 임베딩 유사도만 사용, Intent 분석 없음

**해결**: Router Agent 구현
```python
# Intent 분류
"사냥터" → HUNTING_GROUND (MAP/MONSTER 우선)
"전직" → CLASS_CHANGE (NPC 우선)
"구매" → ITEM_PURCHASE (ITEM/NPC 우선)
```

### 문제 4-2: Ollama 연결 실패
**증상**: Docker에서 Ollama API 접속 불가 (Connection refused)

**해결**: Fallback 로직 강화
```python
# 키워드 기반 규칙으로 충분히 정확한 분류 가능
def _fallback_classification(self, query: str):
    if "전직" in query:
        return {"intent": "class_change", "categories": ["NPC"]}
    elif "사냥터" in query:
        return {"intent": "hunting_ground", "categories": ["MAP", "MONSTER"]}
    ...
```

---

## 🚀 개선 효과

### Before (Router 없음)
```
Query: "도적 사냥터 추천"
  → 여섯갈래길(MAP) 56점 (최고) ❌
  → 의미 유사도만 사용

Query: "도적 전직 어디서?"
  → 다크로드 검색 결과 없음 ❌
```

### After (Router 적용)
```
Query: "도적 사냥터 추천"
  → Intent: HUNTING_GROUND
  → Category: MAP, MONSTER 우선 검색 ✅

Query: "도적 전직 어디서?"
  → Intent: CLASS_CHANGE
  → Category: NPC 우선 검색 ✅
```

---

## 📝 다음 개선 과제

1. **Q&A 생성 개선**
   - "도적 전직"을 명시적인 Q&A로 추가
   - 직업별 사냥터 Q&A 추가

2. **Neo4j 관계 검색**
   - NPC ↔ MAP 관계
   - ITEM ↔ NPC 관계
   - MONSTER ↔ MAP 관계

3. **Ollama Docker 연결**
   - Router Agent에서 LLM 사용 (더 정확한 Intent 분석)

4. **Context Builder**
   - 여러 DB 결과를 통합
   - 최종 답변 생성

---

## 🔑 핵심 교훈

1. **데이터 정규화는 필수**: 같은 Category는 같은 구조여야 함
2. **Intent 분석이 검색 품질을 결정**: 단순 유사도로는 부족
3. **Docker 환경 설정 중요**: 의존성, 네트워크, 환경변수 체계적 관리
4. **Fallback 전략 필수**: LLM 실패해도 키워드 기반으로 작동 가능
5. **Q&A 설계가 의미 검색의 핵심**: 질문-답변 형식으로 구조화

---

*최종 업데이트: 2026-02-02*
