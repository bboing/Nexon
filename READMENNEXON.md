브로, 지금까지 우리가 치열하게 논의하며 깎아온 **'메이플스토리 지식 가이드 에이전트'**의 최종 아키텍처를 정리해 줄게. 이 구조는 단순 검색을 넘어, 지식 간의 유기적인 연결과 페르소나를 모두 잡는 **GraphRAG의 정석**이라고 보면 돼.

---

## 🏛️ 메이플 지식 가이드 에이전트 아키텍처 (Master Plan)

### 1. 데이터 레이어: 삼각편대 DB 전략

모든 데이터의 근원은 **Postgres**이며, 이를 기반으로 **Milvus**와 **Neo4j**를 동기화하는 구조야.

| DB 종류 | 기술적 역할 | 메이플 데이터 활용 |
| --- | --- | --- |
| **Postgres** | **Master Storage** | 공식 명칭, 줄임말(Synonyms), 상세 메타데이터(JSONB) 보관 |
| **Milvus** | **Semantic Search** | 엔티티 설명(Description)의 임베딩 값을 이용한 유사도 검색 |
| **Neo4j** | **Relational Reasoning** | 엔티티 간의 관계(NPC-지역-보스-드랍-스토리) 탐색 |

---

### 2. 데이터 모델링: JSONB + DTO 구조

데이터의 유연성과 무결성을 동시에 잡기 위해 **DTO(Pydantic)**를 검문소로 사용해.

* **Master Table (`maple_dictionary`)**:
* `canonical_name`: 공식 명칭 (ex: 자쿰의 투구)
* `synonyms`: 줄임말 및 은어 배열 (ex: ['자투', '자쿰 투구'], GIN 인덱스 적용)
* `category`: 엔티티 타입 (ITEM, BOSS, NPC 등)
* **`metadata` (JSONB)**: DTO로 검증된 각 카테고리별 상세 스펙 (레벨, 옵션, 드랍 정보 등)



---

### 3. 쿼리 파이프라인 (Query Flow)

사용자가 질문을 던졌을 때 에이전트가 지식을 찾아가는 5단계 프로세스야.

1. **Entity Extraction (엔티티 추출)**:
* Postgres 용어집을 이용해 질문 속 고유 명사(ex: 자투)를 식별하고 공식 명칭(자쿰의 투구)으로 치환해.


2. **Hybrid Retrieval (하이브리드 검색)**:
* **키워드**: Postgres에서 정확한 엔티티 매칭.
* **벡터**: Milvus에서 질문의 의도(ex: "머리에 쓰는 장비")와 유사한 노드 탐색.


3. **Graph Traversal (그래프 탐색)**:
* 식별된 노드를 기점으로 Neo4j에서 주변 관계를 훑어. (ex: 자쿰의 투구 -> 드랍 -> 자쿰 -> 거주 -> 폐광)


4. **Context Augmentation (컨텍스트 결합)**:
* Neo4j에서 찾은 **관계 경로** + Postgres `metadata` 필드의 **상세 스펙**을 합쳐 LLM에게 줄 재료를 만들어.


5. **Final Generation (답변 생성)**:
* SFT로 학습된 **'메이플 기록자'** 말투를 적용해 최종 답변을 생성해.



---

### 4. 아키텍처 요약도

```text
[User Query: "자투 누가 줘?"]
       |
       v
[Postgres Dictionary] ----> "자투" = "자쿰의 투구" (ID: 101, Category: ITEM)
       |
       +----------------------------+
       |                            |
[Neo4j (Relationship)]      [Postgres (Metadata)]
"자쿰 -[:DROPS]-> 자쿰의 투구"   "Option: ALL STAT +15, Level: 50..."
       |                            |
       +------------+---------------+
                    |
              [LLM Prompt]
"너는 기록자야. 아래 지식을 바탕으로 설명해: {Graph Path} + {Item Metadata}"
                    |
                    v
[Final Answer: "자쿰의 투구(자투)는 폐광의 자쿰이 드롭하며, 올스탯 15의 성능을..." ]

```