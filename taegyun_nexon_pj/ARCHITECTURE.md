# System Architecture

## 🏗️ High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Application                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                                                                   │
│  ┌──────────────────┐                                           │
│  │  API Endpoints   │  /api/v1/qa                               │
│  │  (api/main.py)   │                                           │
│  └────────┬─────────┘                                           │
│           │                                                       │
│           ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Router Agent                                 │   │
│  │  ┌────────────────────────────────────────────┐          │   │
│  │  │ 1. Intent Analysis                         │          │   │
│  │  │    - Query Type (GENERAL/SPECIFIC/RELATION)│          │   │
│  │  │    - Entity Categories (NPC/MAP/ITEM/...)  │          │   │
│  │  │    - Search Strategy                        │          │   │
│  │  └────────────────────────────────────────────┘          │   │
│  │                         │                                  │   │
│  │                         ▼                                  │   │
│  │  ┌────────────────────────────────────────────┐          │   │
│  │  │ 2. Query Planning                          │          │   │
│  │  │    Creates multi-step execution plan       │          │   │
│  │  │    [Step1: SQL], [Step2: Graph], ...       │          │   │
│  │  └────────────────────────────────────────────┘          │   │
│  └──────────────────────────────────────────────────────────┘   │
│           │                                                       │
│           ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Hybrid Search Orchestrator                      │   │
│  │                                                            │   │
│  │   Parallel Execution (asyncio.gather):                    │   │
│  │                                                            │   │
│  │   ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │   │
│  │   │ PostgreSQL  │  │    Neo4j     │  │    Milvus     │   │   │
│  │   │  Searcher   │  │   Searcher   │  │  Retriever    │   │   │
│  │   └──────┬──────┘  └──────┬───────┘  └───────┬───────┘   │   │
│  │          │                 │                   │            │   │
│  │          │                 │                   │            │   │
│  │   ┌──────▼─────────────────▼───────────────────▼───────┐   │   │
│  │   │         Result Merging & Deduplication            │   │   │
│  │   └────────────────────────┬───────────────────────────┘   │   │
│  └────────────────────────────┼───────────────────────────────┘   │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Answer Generator                             │    │
│  │  ┌────────────────────────────────────────────┐          │    │
│  │  │ 1. Context Formatting                      │          │    │
│  │  │    - Schema-aware structure                │          │    │
│  │  │    - Relevant fields only                  │          │    │
│  │  └────────────────────────────────────────────┘          │    │
│  │                         │                                  │    │
│  │                         ▼                                  │    │
│  │  ┌────────────────────────────────────────────┐          │    │
│  │  │ 2. Prompt Engineering                      │          │    │
│  │  │    - System prompt (role definition)       │          │    │
│  │  │    - Context injection                     │          │    │
│  │  │    - Answer guidelines                     │          │    │
│  │  └────────────────────────────────────────────┘          │    │
│  │                         │                                  │    │
│  │                         ▼                                  │    │
│  │  ┌────────────────────────────────────────────┐          │    │
│  │  │ 3. LLM Call (Ollama)                       │          │    │
│  │  │    - Async invocation                      │          │    │
│  │  │    - Streaming support                     │          │    │
│  │  └────────────────────────────────────────────┘          │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Response (JSON)   │
                    │   - answer          │
                    │   - confidence      │
                    │   - sources         │
                    └─────────────────────┘
```

## 🗄️ Data Layer Architecture

### Database Roles

```
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL (Primary Store)                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  maple_dictionary Table                                  │    │
│  │  - id, canonical_name, synonyms[], category             │    │
│  │  - description (text)                                    │    │
│  │  - detail_data (JSONB)                                   │    │
│  │    {                                                     │    │
│  │      "location": "헤네시스",                              │    │
│  │      "resident_npcs": [...],                             │    │
│  │      "drops": [{item, rate}],                            │    │
│  │      ...                                                 │    │
│  │    }                                                     │    │
│  │  - search_vector (tsvector) for full-text search        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Use Cases:                                                      │
│  - Keyword-based exact/fuzzy search                              │
│  - Synonym mapping                                               │
│  - Category filtering                                            │
│  - Field-specific queries (location, level, etc.)                │
└───────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Neo4j (Graph Store)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Nodes: NPC, MAP, ITEM, MONSTER                          │    │
│  │  Relationships:                                          │    │
│  │    - (NPC)-[:LOCATED_IN]->(MAP)                          │    │
│  │    - (MONSTER)-[:LOCATED_IN]->(MAP)                      │    │
│  │    - (MONSTER)-[:DROPS {rate}]->(ITEM)                   │    │
│  │    - (NPC)-[:SELLS {price}]->(ITEM)                      │    │
│  │    - (MAP)-[:CONNECTS_TO {direction}]->(MAP)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Use Cases:                                                      │
│  - Relationship traversal ("NPCs in Perion")                     │
│  - Path finding (MAP → MAP connections)                          │
│  - Multi-hop queries (Item → Monster → Location)                 │
└───────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Milvus (Vector Store)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Collections: maple_qa                                   │    │
│  │  - vector (embedding)                                    │    │
│  │  - entity_id (reference to PostgreSQL)                   │    │
│  │  - text (original description)                           │    │
│  │  - metadata (category, tags, etc.)                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Use Cases:                                                      │
│  - Semantic similarity search                                    │
│  - Query expansion (find similar entities)                       │
│  - Fallback when keyword search fails                            │
└───────────────────────────────────────────────────────────────────┘
```

## 🔄 Query Execution Flow

### Example: "페리온에 있는 NPC는 누구?"

```
1. Query Reception
   │
   ├─> FastAPI endpoint receives query
   │
2. Router Agent Analysis
   │
   ├─> Intent: RELATION (MAP → NPC)
   ├─> Categories: [MAP, NPC]
   ├─> Strategy: RELATION
   ├─> Plan:
   │     Step 1: SQL_DB → Find MAP "페리온"
   │     Step 2: GRAPH_DB → Find NPCs in that MAP
   │
3. Hybrid Search Execution (Parallel)
   │
   ├─> PostgreSQL Searcher
   │     - Search for "페리온" in category=MAP
   │     - Return: Map entity with resident_npcs in detail_data
   │
   ├─> Neo4j Searcher (if needed)
   │     - Query: MATCH (n:NPC)-[:LOCATED_IN]->(m:MAP {name: "페리온"})
   │     - Return: NPC nodes
   │
   ├─> Milvus (optional, for expansion)
   │     - Semantic search for similar queries
   │
4. Result Merging
   │
   ├─> Combine results from all sources
   ├─> Deduplicate by entity ID
   ├─> Enrich with detail_data from PostgreSQL
   │
5. Answer Generation
   │
   ├─> Format context with NPC details
   ├─> Create prompt with system instructions
   ├─> LLM generates natural language response
   │
6. Response
   │
   └─> {
         "answer": "페리온에는 다크로드, 헬레나, 피터 등의 NPC가 있습니다...",
         "confidence": 0.95,
         "sources": ["MAP:페리온", "NPC:다크로드", ...]
       }
```

## 🧠 Key Design Patterns

### 1. Async/Await Throughout

All I/O operations use async:
- Database queries: `AsyncSession`, `AsyncGraphDatabase`
- LLM calls: `ainvoke()`, `astream()`
- Parallel execution: `asyncio.gather()`

Benefits:
- Non-blocking I/O
- High concurrency
- Efficient resource utilization

### 2. Lazy Initialization

Components initialize on first use:
```python
class MapleKeywordExtractor:
    async def _ensure_initialized(self):
        if not self._initialized:
            await self.mapper.load_mappings()
            self._initialized = True
```

### 3. Router-Based Query Planning

Router agent creates execution plans dynamically:
- Analyzes query intent
- Determines optimal database combinations
- Creates multi-step plans for complex queries

### 4. Schema-Aware Generation

Answer generator understands entity schemas:
- Different formatting for NPC vs ITEM vs MAP
- Field-specific prompting (location, drops, level)
- Prevents hallucination by strict context boundaries

### 5. Observability-First

Integrated tracing:
- Langfuse for LLM call tracking
- Request/response logging
- Performance metrics

## 🔧 Technology Decisions

### Why Async?
- FastAPI is async-native
- Multiple database calls can run in parallel
- Better handling of concurrent requests

### Why Hybrid Search?
- **SQL**: Fast exact/fuzzy matching, structured queries
- **Graph**: Relationship traversal, multi-hop queries
- **Vector**: Semantic understanding, query expansion

Each database type handles what it does best.

### Why Local LLM (Ollama)?
- Data privacy (no external API calls)
- Cost-effective for high volume
- Low latency (no network round-trip)
- Customizable models

### Why Router Agent?
- Flexible query handling (not rigid if-else)
- Adapts to query complexity
- Easy to extend with new patterns

## 📊 Performance Characteristics

- **Typical query latency**: 500-2000ms
  - Router analysis: 100-300ms
  - DB searches (parallel): 50-200ms
  - LLM generation: 300-1500ms

- **Throughput**: 10-50 req/sec (single instance)
  - Limited by LLM inference speed
  - Can scale horizontally with load balancer

- **Data scale**:
  - PostgreSQL: 1000s of entities
  - Neo4j: 10000s of relationships
  - Milvus: 100000s of vectors

## 🚀 Scalability Considerations

### Horizontal Scaling
- Stateless FastAPI instances
- Load balancer (Nginx)
- Shared database backends

### Caching Strategy
- Redis for frequently accessed entities
- TTL-based invalidation
- Query result caching

### Database Optimization
- PostgreSQL: Indexes on `canonical_name`, `category`, `search_vector`
- Neo4j: Indexes on node labels and relationship types
- Milvus: IVF_FLAT index for vector search

---

*This architecture is designed for production deployment while maintaining clarity and maintainability.*
