#!/usr/bin/env python3
"""
Search Agent 간단 테스트 (디버그용)
"""
import sys
from pathlib import Path

# 경로 설정
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LANGCHAIN_APP_DIR = PROJECT_ROOT / "langchain_app"
sys.path.insert(0, str(LANGCHAIN_APP_DIR))

# .env 로드
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

print("✅ 1. 환경 설정 완료")

# Import
from database.session import SessionLocal
from src.retrievers.db_searcher import MapleDBSearcher

print("✅ 2. 모듈 import 완료")

# DB 연결 테스트
db = SessionLocal()
print("✅ 3. DB 연결 완료")

# Searcher 테스트
searcher = MapleDBSearcher(db)
print("✅ 4. Searcher 생성 완료")

# 검색 테스트
print("\n" + "="*80)
print("🔍 검색 테스트: '아이스진'")
print("="*80)

results = searcher.search("아이스진", limit=3)
print(f"\n📊 검색 결과: {len(results)}개\n")

for idx, result in enumerate(results, 1):
    data = result["data"]
    print(f"{idx}. {data['canonical_name']} ({data['category']})")
    print(f"   점수: {result['score']}점")
    print(f"   설명: {data.get('description', '없음')[:50]}...")
    
    detail = data.get("detail_data", {})
    if detail and data['category'] == 'ITEM':
        obtainable = detail.get('obtainable_from', [])
        if obtainable:
            print(f"   획득: {', '.join(obtainable)}")
    print()

print("="*80)
print("✅ 5. DB 검색 완료!")
print("\n이제 LLM 테스트를 해볼까요?")
print("실행: python scripts/test_llm.py")

db.close()
