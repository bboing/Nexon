# 검색 알고리즘 Option 구현 노트

## 파일 구조

```
hybrid_searcher.py          # 현재 (Plan 기반)
hybrid_searcher_option2.py  # Option 2 (임계값 기반)
hybrid_searcher_option3.py  # Option 3 (Intent 기반) - 구현 중
```

## Option 2: 임계값 기반 (구현 완료)

### 핵심 로직

```python
async def search(self, query, limit=10, threshold=5):
    # 1. PostgreSQL + Milvus 병렬
    pg, milvus = await asyncio.gather(
        _postgres_search(query),
        _milvus_search(query)
    )
    
    # 2. 임계값 체크
    if len(pg) + len(milvus) < threshold:
        neo4j = await _neo4j_search(query)
    else:
        neo4j = []
    
    # 3. RRF 병합
    return _apply_rrf({
        "PostgreSQL": pg,
        "Milvus": milvus,
        "Neo4j": neo4j
    })
```

### 필요한 헬퍼 메서드

- `_neo4j_simple_search()`: 간단한 Neo4j 검색
- `_apply_rrf()`: 기존 RRF 메서드 재사용

## Option 3: Intent 기반 (구현 필요)

### 핵심 로직

```python
RELATION_INTENTS = {
    "npc_location", "item_drop", "monster_location",
    "item_purchase", "class_change"
}

async def search(self, query, limit=10):
    # 1. Intent 분류 (가볍게)
    intent = await self._classify_intent(query)
    
    # 2. PostgreSQL + Milvus 항상 병렬
    pg_task = _postgres_search(query)
    milvus_task = _milvus_search(query)
    
    # 3. 관계 Intent면 Neo4j도 병렬
    if intent in RELATION_INTENTS:
        neo4j_task = _neo4j_search(query)
        pg, milvus, neo4j = await asyncio.gather(
            pg_task, milvus_task, neo4j_task
        )
    else:
        pg, milvus = await asyncio.gather(pg_task, milvus_task)
        neo4j = []
    
    # 4. RRF 병합
    return _apply_rrf({
        "PostgreSQL": pg,
        "Milvus": milvus,
        "Neo4j": neo4j
    })
```

### 필요한 메서드

#### 1. `_classify_intent()` - 가벼운 Intent 분류

```python
async def _classify_intent(self, query: str) -> str:
    """
    LLM으로 Intent만 분류 (Plan 생성 X)
    
    Plan 대비 빠름:
    - Plan: 500 토큰 응답
    - Intent: 10 토큰 응답
    """
    if not self.router:
        return "general"
    
    prompt = f"""
다음 질문의 Intent를 1단어로 분류:

class_change: 전직
npc_location: NPC 위치
item_drop: 아이템 드랍
monster_location: 몬스터 위치
item_purchase: 아이템 구매
map_connection: 맵 이동
general: 일반

질문: {query}
Intent:"""
    
    response = await self.router.llm.ainvoke(prompt)
    intent = response.content.strip().lower()
    
    return intent if intent in self.RELATION_INTENTS else "general"
```

## 평가 스크립트 업데이트

### `evaluate_search.py` 수정 필요

```python
# HybridSearcher import 선택
if args.option == 2:
    from src.retrievers.hybrid_searcher_option2 import HybridSearcher
elif args.option == 3:
    from src.retrievers.hybrid_searcher_option3 import HybridSearcher
else:
    from src.retrievers.hybrid_searcher import HybridSearcher
```

### 실행 예시

```bash
# 현재 (Plan)
python scripts/evaluate_search.py --plan

# Option 2
python scripts/evaluate_search.py --option 2

# Option 3
python scripts/evaluate_search.py --option 3

# 비교
python scripts/evaluate_search.py --mode compare
```

## 구현 우선순위

1. ✅ Option 2 search 메서드 구현
2. ⬜ Option 2 `_neo4j_simple_search()` 추가
3. ⬜ Option 3 `_classify_intent()` 구현
4. ⬜ Option 3 search 메서드 완성
5. ⬜ `evaluate_search.py` 옵션 선택 기능

## 예상 성능

| 메트릭 | 현재 (Plan) | Option 2 | Option 3 |
|--------|------------|----------|----------|
| 속도 | 2.8s | 2.1s | 2.3s |
| MRR | 0.68 | 0.70 | 0.85 |
| nDCG@10 | 0.75 | 0.72 | 0.88 |
| LLM 비용 | 높음 (Plan) | 없음 | 중간 (Intent) |

## 다음 단계

1. Option 2, 3 완전히 구현
2. 20개 테스트셋으로 평가
3. 결과 비교표 작성
4. 최적 옵션 선택
