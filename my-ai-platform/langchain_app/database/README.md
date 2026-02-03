# 📂 Database Package

PostgreSQL + SQLAlchemy 통합 데이터베이스 패키지

---

## 📁 구조

```
database/
├── __init__.py              # 패키지 진입점
├── base.py                  # Base 클래스 정의
├── session.py               # DB 세션 관리
├── README.md                # 이 문서
│
├── models/                  # SQLAlchemy 모델들
│   ├── __init__.py
│   ├── document.py          # 문서 모델
│   ├── user.py              # 사용자 모델
│   └── chat_history.py      # 채팅 히스토리 모델
│
└── crud/                    # CRUD 작업
    ├── __init__.py
    ├── document.py          # 문서 CRUD
    ├── user.py              # 사용자 CRUD
    └── chat_history.py      # 채팅 히스토리 CRUD
```

---

## 🚀 사용 방법

### 1️⃣ **DB 초기화 (테이블 생성)**

```python
from database.session import init_db

# 앱 시작 시 실행
init_db()
```

### 2️⃣ **FastAPI에서 사용**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from database.crud import document

router = APIRouter()

@router.post("/documents")
async def create_document(
    title: str,
    content: str,
    db: Session = Depends(get_db)
):
    """문서 생성"""
    doc = document.create_document(
        db=db,
        title=title,
        content=content
    )
    return {"id": doc.id, "title": doc.title}


@router.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """문서 목록 조회"""
    docs = document.get_documents(db, skip=skip, limit=limit)
    return {"documents": docs, "count": len(docs)}


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """문서 조회"""
    doc = document.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
```

### 3️⃣ **직접 세션 사용**

```python
from database import SessionLocal
from database.crud import document

# 세션 생성
db = SessionLocal()

try:
    # 문서 생성
    doc = document.create_document(
        db=db,
        title="제목",
        content="내용"
    )
    print(f"Created: {doc.id}")
    
    # 문서 조회
    docs = document.get_documents(db, limit=10)
    print(f"Total: {len(docs)}")
    
finally:
    db.close()
```

---

## 📊 테이블 구조

### **documents** (문서)
```sql
id              VARCHAR(36)  PRIMARY KEY
title           VARCHAR(500) NOT NULL
content         TEXT         NOT NULL
file_path       VARCHAR(1000)
file_type       VARCHAR(50)
file_size       INTEGER
is_processed    BOOLEAN      DEFAULT FALSE
chunk_count     INTEGER      DEFAULT 0
source          VARCHAR(200)
author          VARCHAR(200)
tags            TEXT         -- JSON
created_at      TIMESTAMP    DEFAULT NOW()
updated_at      TIMESTAMP
processed_at    TIMESTAMP
```

### **users** (사용자)
```sql
id              VARCHAR(36)  PRIMARY KEY
username        VARCHAR(100) UNIQUE NOT NULL
email           VARCHAR(255) UNIQUE NOT NULL
hashed_password VARCHAR(255)
full_name       VARCHAR(200)
is_active       BOOLEAN      DEFAULT TRUE
is_superuser    BOOLEAN      DEFAULT FALSE
created_at      TIMESTAMP    DEFAULT NOW()
updated_at      TIMESTAMP
last_login      TIMESTAMP
```

### **chat_history** (채팅 히스토리)
```sql
id              VARCHAR(36)  PRIMARY KEY
session_id      VARCHAR(100) NOT NULL
user_id         VARCHAR(36)  FOREIGN KEY -> users.id
role            VARCHAR(20)  NOT NULL  -- user, assistant, system
content         TEXT         NOT NULL
message_index   INTEGER      NOT NULL
model           VARCHAR(100)
tokens_used     INTEGER
latency_ms      INTEGER
rag_used        VARCHAR(10)
retrieved_docs  TEXT         -- JSON
created_at      TIMESTAMP    DEFAULT NOW()
```

---

## 🔧 마이그레이션 (Alembic)

현재는 `init_db()`로 테이블을 자동 생성하지만, 운영 환경에서는 **Alembic**을 사용하는 것을 권장합니다.

### Alembic 설정 (선택사항)

```bash
# Alembic 설치
pip install alembic

# 초기화
cd langchain_app
alembic init alembic

# alembic.ini 수정 (sqlalchemy.url 설정)
# alembic/env.py 수정 (Base import)

# 마이그레이션 생성
alembic revision --autogenerate -m "Create initial tables"

# 마이그레이션 적용
alembic upgrade head
```

---

## 💡 베스트 프랙티스

### 1. **트랜잭션 관리**
```python
from database import SessionLocal

db = SessionLocal()
try:
    # 여러 작업을 하나의 트랜잭션으로
    doc1 = create_document(db, "Title 1", "Content 1")
    doc2 = create_document(db, "Title 2", "Content 2")
    db.commit()  # 한 번에 커밋
except Exception as e:
    db.rollback()  # 에러 시 롤백
    raise
finally:
    db.close()
```

### 2. **FastAPI Dependency 사용**
```python
# ✅ 권장: Depends 사용
@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

# ❌ 비권장: 직접 세션 생성
@router.get("/items")
async def get_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()  # 에러 시 닫히지 않음!
    return items
```

### 3. **N+1 쿼리 방지**
```python
# ❌ N+1 문제
docs = db.query(Document).all()
for doc in docs:
    print(doc.user.name)  # 각 문서마다 쿼리 발생!

# ✅ Eager Loading
from sqlalchemy.orm import joinedload
docs = db.query(Document).options(
    joinedload(Document.user)
).all()
```

---

## 🔍 디버깅

### SQL 쿼리 로그 보기
```python
# session.py에서 echo=True로 변경
engine = create_engine(
    settings.postgres_url,
    echo=True  # ← SQL 쿼리 출력
)
```

### 연결 테스트
```python
from database import engine

try:
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## 📚 참고 자료

- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [FastAPI + SQLAlchemy 가이드](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Alembic 마이그레이션](https://alembic.sqlalchemy.org/)
