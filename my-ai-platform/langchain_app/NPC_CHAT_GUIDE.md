# 🎮 NPC Chat API 사용 가이드

메이플스토리 NPC와 대화하는 시스템입니다.

---

## 🏗️ 아키텍처

```
[사용자 질문: "밍밍부인, 스탄 장로 아세요?"]
         ↓
    NPC Chat API
         ↓
1. DB에서 NPC 조회 (PostgreSQL)
   → SELECT * FROM npcs WHERE npc_name = '밍밍부인'
         ↓
2. System 프롬프트 구성
   → "당신은 '헤네시스'에 거주하는 NPC '밍밍부인'입니다. 
       헤네시스 장로 스탄의 부인..."
         ↓
3. LLM 호출 (파인튜닝된 모델)
   → System + User Message
         ↓
4. 응답 반환
   → "어머, 제 남편을 아시나요?..."
```

---

## 🚀 빠른 시작

### 1️⃣ DB 테이블 생성

```bash
# Docker 재시작 시 자동으로 테이블 생성됨
docker compose -f docker-compose.integrated.yml restart langchain-api

# 또는 수동으로
docker exec ai-langchain-api python -c "from database.session import init_db; init_db()"
```

### 2️⃣ NPC 데이터 import

```bash
# API 호출
curl -X POST "http://localhost:8000/api/npc/import" \
  -H "Content-Type: application/json"

# 결과
{
  "status": "success",
  "imported": 50,
  "message": "50개 NPC가 import되었습니다."
}
```

### 3️⃣ NPC와 대화

```bash
curl -X POST "http://localhost:8000/api/npc/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "npc_name": "밍밍부인",
    "message": "장로 스탄님을 아시나요?"
  }'

# 응답
{
  "npc_name": "밍밍부인",
  "city": "헤네시스",
  "message": "장로 스탄님을 아시나요?",
  "response": "어머, 제 남편을 아시나요? 겉으로는 엄격해 보여도 속은 따뜻한 분이랍니다...",
  "session_id": null,
  "rag_used": true,
  "latency_ms": 1234
}
```

---

## 📋 API 엔드포인트

### **POST /api/npc/chat**
NPC와 대화

**Request:**
```json
{
  "npc_name": "밍밍부인",
  "city": "헤네시스",  // 선택 (동명이인 방지)
  "message": "안녕하세요?",
  "session_id": "session-123",  // 선택 (대화 추적)
  "use_rag": true
}
```

**Response:**
```json
{
  "npc_name": "밍밍부인",
  "city": "헤네시스",
  "message": "안녕하세요?",
  "response": "어서 오세요, 여행자님!",
  "session_id": "session-123",
  "rag_used": true,
  "retrieved_context": null,
  "latency_ms": 1234
}
```

### **GET /api/npc/list**
NPC 목록 조회

**Query Params:**
- `city`: 도시 필터 (선택)
- `skip`: offset (페이지네이션)
- `limit`: limit (기본 100)

**Response:**
```json
{
  "npcs": [...],
  "total": 50,
  "cities": ["헤네시스", "페리온", "엘리니아", "커닝시티"]
}
```

### **GET /api/npc/{npc_name}**
NPC 상세 정보

**Response:**
```json
{
  "id": "uuid...",
  "npc_name": "밍밍부인",
  "city": "헤네시스",
  "instruction": "헤네시스 장로 스탄의 부인...",
  "description": "...",
  "keywords": "밍밍부인,헤네시스",
  "metadata": {...},
  "sample_conversations": [...]
}
```

### **POST /api/npc/search**
NPC 검색

**Request:**
```json
{
  "keyword": "버섯",
  "limit": 10
}
```

**Response:**
```json
{
  "keyword": "버섯",
  "results": [
    {"npc_name": "브루스", "city": "헤네시스", ...}
  ],
  "count": 1
}
```

### **GET /api/npc/cities/stats**
도시별 통계

**Response:**
```json
{
  "total_cities": 4,
  "total_npcs": 50,
  "cities": {
    "헤네시스": 20,
    "페리온": 15,
    "엘리니아": 10,
    "커닝시티": 5
  }
}
```

---

## 🎯 사용 시나리오

### **1. 일반 대화**
```python
import requests

response = requests.post("http://localhost:8000/api/npc/chat", json={
    "npc_name": "밍밍부인",
    "message": "안녕하세요?"
})

print(response.json()["response"])
# → "어서 오세요, 여행자님!"
```

### **2. 도시별 NPC 조회**
```python
response = requests.get("http://localhost:8000/api/npc/list?city=헤네시스")
npcs = response.json()["npcs"]

for npc in npcs:
    print(f"{npc['npc_name']}: {npc['instruction'][:50]}...")
```

### **3. NPC 검색**
```python
response = requests.post("http://localhost:8000/api/npc/search", json={
    "keyword": "전사"
})

results = response.json()["results"]
# → 전사 관련 NPC들
```

---

## 🔧 환경 설정

### `.env` 파일에 추가:
```bash
# Neo4j
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

---

## 🎯 다음 단계

### **Phase 1 완료:**
- ✅ Neo4j Docker 추가
- ✅ NPC 테이블 (SQLAlchemy)
- ✅ NPC CRUD
- ✅ NPC Chat API

### **Phase 2 구현 필요:**
- [ ] Entity Extractor (용어 추출)
- [ ] Hybrid Retriever (Postgres + Milvus)
- [ ] Graph Traverser (Neo4j)
- [ ] Context Augmentation
- [ ] 세계관 데이터 파인튜닝

---

**테스트하세요!** 🎉

```bash
# 1. Docker 재시작
docker compose -f docker-compose.integrated.yml up -d

# 2. NPC import
curl -X POST http://localhost:8000/api/npc/import

# 3. 대화 테스트
curl -X POST http://localhost:8000/api/npc/chat \
  -H "Content-Type: application/json" \
  -d '{"npc_name": "밍밍부인", "message": "안녕하세요?"}'
```
