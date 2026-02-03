# Scripts

데이터 관리 및 테스트를 위한 스크립트 모음 (로컬 실행용)

## 📦 설치

```bash
cd scripts
pip install -r requirements.txt
```

## 🔧 스크립트 목록

### 데이터 관리
- `import_data.py` - PostgreSQL 데이터 임포트
- `delete_data.py` - 데이터 삭제
- `sync_to_milvus.py` - PostgreSQL → Milvus Q&A 동기화

### 테스트
- `test_db_search.py` - DB 검색 테스트
- `test_search_agent.py` - Search Agent 테스트
- `test_router.py` - Router Agent 테스트
- `test_hybrid_search.py` - Hybrid Searcher 테스트
- `test_milvus_sync.py` - Milvus 동기화 테스트
- `compare_router_models.py` - Router 모델 비교

### 시스템 관리 (Shell Scripts)
- `start-integrated.sh` - Docker 통합 환경 시작
- `stop-all.sh` - 모든 서비스 중지
- `status.sh` - 서비스 상태 확인
- `backup.sh` - 백업
- `cleanup.sh` - 정리

## 🚀 사용 예시

```bash
# 1. 의존성 설치 (최초 1회)
pip install -r requirements.txt

# 2. 데이터 임포트
python import_data.py data/sample.json

# 3. Milvus 동기화
python sync_to_milvus.py --drop

# 4. 테스트
python test_search_agent.py "도적이 되려면?"
```

## ⚠️ 주의사항

- 이 스크립트들은 **로컬 환경**에서 실행됩니다
- Docker 컨테이너 안에서 실행할 필요 **없음**
- `.env` 파일이 프로젝트 루트에 있어야 함
- PostgreSQL, Milvus 등 서비스는 Docker로 실행 중이어야 함

## 🐳 vs Docker

| 구분 | 실행 환경 | 의존성 파일 |
|------|----------|------------|
| **FastAPI 앱** | Docker | `langchain_app/requirements.txt` |
| **Scripts** | Local | `scripts/requirements.txt` |

완전히 독립적으로 관리됩니다!
