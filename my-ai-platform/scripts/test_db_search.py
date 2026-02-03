#!/usr/bin/env python3
"""
DB Searcher 테스트 스크립트
"""
import sys
from pathlib import Path
from typing import Optional

# 경로 설정
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LANGCHAIN_APP_DIR = PROJECT_ROOT / "langchain_app"
sys.path.insert(0, str(LANGCHAIN_APP_DIR))

# .env 로드
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Import
from database.session import SessionLocal
from src.retrievers.db_searcher import MapleDBSearcher
import json


def test_search(keyword: str, category: Optional[str] = None):
    """검색 테스트"""
    db = SessionLocal()
    try:
        searcher = MapleDBSearcher(db)
        
        print("\n" + "="*80)
        print(f"🔍 검색어: '{keyword}'" + (f" (카테고리: {category})" if category else ""))
        print("="*80)
        
        results = searcher.search(keyword, category=category, limit=5)
        
        if not results:
            print("\n❌ 검색 결과 없음")
            return
        
        print(f"\n📊 검색 결과: {len(results)}개\n")
        
        for idx, result in enumerate(results, 1):
            data = result["data"]
            print(f"{idx}. [{result['score']}점] {data['canonical_name']}")
            print(f"   📁 카테고리: {data['category']}")
            print(f"   🏷️  동의어: {', '.join(data.get('synonyms', []))}")
            print(f"   📝 설명: {data.get('description', '없음')[:80]}...")
            print(f"   🎯 매칭 타입: {result['match_type']}")
            print()
        
        print("="*80)
        
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_related_search(canonical_name: str):
    """연관 엔티티 검색 테스트"""
    db = SessionLocal()
    try:
        searcher = MapleDBSearcher(db)
        
        print("\n" + "="*80)
        print(f"🔗 연관 검색: '{canonical_name}'")
        print("="*80)
        
        related = searcher.get_related_entities(canonical_name)
        
        if not related:
            print("\n❌ 엔티티를 찾을 수 없습니다.")
            return
        
        source = related["source"]
        print(f"\n📌 기준 엔티티: {source['canonical_name']} ({source['category']})")
        print(f"   {source.get('description', '')}\n")
        
        # 연관 NPC
        if related["related_npcs"]:
            print(f"👥 연관 NPC ({len(related['related_npcs'])}개):")
            for npc in related["related_npcs"]:
                print(f"   - {npc['data']['canonical_name']}")
        
        # 연관 아이템
        if related["related_items"]:
            print(f"🎒 연관 아이템 ({len(related['related_items'])}개):")
            for item in related["related_items"]:
                print(f"   - {item['data']['canonical_name']}")
        
        # 연관 맵
        if related["related_maps"]:
            print(f"🗺️  연관 맵 ({len(related['related_maps'])}개):")
            for map_item in related["related_maps"]:
                print(f"   - {map_item['data']['canonical_name']}")
        
        # 연관 몬스터
        if related["related_monsters"]:
            print(f"👾 연관 몬스터 ({len(related['related_monsters'])}개):")
            for monster in related["related_monsters"]:
                print(f"   - {monster['data']['canonical_name']}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ 연관 검색 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📚 사용법:")
        print("  python test_db_search.py <키워드>                 # 기본 검색")
        print("  python test_db_search.py <키워드> <카테고리>      # 카테고리 필터")
        print("  python test_db_search.py --related <이름>         # 연관 검색")
        print("\n예시:")
        print("  python test_db_search.py 아이스진")
        print("  python test_db_search.py 헤네시스 MAP")
        print("  python test_db_search.py --related 주황버섯")
        sys.exit(1)
    
    if sys.argv[1] == "--related":
        # 연관 검색
        if len(sys.argv) < 3:
            print("❌ 엔티티 이름을 입력하세요.")
            sys.exit(1)
        test_related_search(sys.argv[2])
    else:
        # 기본 검색
        keyword = sys.argv[1]
        category = sys.argv[2] if len(sys.argv) > 2 else None
        test_search(keyword, category)
