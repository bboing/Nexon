#!/usr/bin/env python3
"""
Database 데이터 삭제 스크립트 (SQLAlchemy)
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

# DB 세션
from database.session import SessionLocal
from database.models.maple_dictionary import MapleDictionary

def delete_by_name(canonical_name: str, force: bool = False):
    """canonical_name으로 삭제"""
    db = SessionLocal()
    try:
        # 삭제할 항목 찾기
        item = db.query(MapleDictionary).filter_by(canonical_name=canonical_name).first()
        
        if item:
            print("\n" + "="*60)
            print(f"🗑️  삭제 대상 항목 (1개)")
            print("="*60)
            print(f"📌 이름: {item.canonical_name}")
            print(f"📁 카테고리: {item.category.value}")
            print(f"📝 설명: {item.description}")
            print(f"🏷️  동의어: {', '.join(item.synonyms) if item.synonyms else '없음'}")
            print(f"📅 생성일: {item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '정보 없음'}")
            print("="*60)
            
            # 삭제 확인 (force 옵션이 있으면 생략)
            if not force:
                confirm = input("\n❓ 정말 삭제하시겠습니까? (y/N): ").strip()
            else:
                confirm = 'y'
                print("\n⚡ --force 옵션: 자동 삭제")
            
            if confirm.lower() == 'y':
                db.delete(item)
                db.commit()
                print("✅ 삭제 완료!")
            else:
                print("❌ 삭제 취소됨")
        else:
            print(f"\n❌ '{canonical_name}' 항목을 찾을 수 없습니다.")
    except Exception as e:
        db.rollback()
        print(f"\n❌ 삭제 실패: {e}")
    finally:
        db.close()

def delete_by_names(names: list):
    """여러 항목 한번에 삭제"""
    db = SessionLocal()
    try:
        # 삭제할 항목 확인
        items = db.query(MapleDictionary)\
            .filter(MapleDictionary.canonical_name.in_(names))\
            .all()
        
        if not items:
            print("\n❌ 삭제할 항목을 찾을 수 없습니다.")
            return
        
        # 찾지 못한 항목 표시
        found_names = {item.canonical_name for item in items}
        not_found = set(names) - found_names
        if not_found:
            print(f"\n⚠️  찾을 수 없는 항목 ({len(not_found)}개):")
            for name in not_found:
                print(f"   - {name}")
        
        print("\n" + "="*60)
        print(f"🗑️  삭제 대상 항목 ({len(items)}개)")
        print("="*60)
        for idx, item in enumerate(items, 1):
            print(f"{idx}. 📌 {item.canonical_name}")
            print(f"   📁 카테고리: {item.category.value}")
            print(f"   📝 설명: {item.description[:50]}..." if len(item.description or '') > 50 else f"   📝 설명: {item.description}")
            print()
        print("="*60)
        
        # 삭제 확인
        confirm = input(f"\n❓ {len(items)}개 항목을 삭제하시겠습니까? (y/N): ").strip()
        if confirm.lower() == 'y':
            deleted_count = db.query(MapleDictionary)\
                .filter(MapleDictionary.canonical_name.in_(names))\
                .delete(synchronize_session=False)
            
            db.commit()
            print(f"\n✅ {deleted_count}개 항목 삭제 완료!")
        else:
            print("\n❌ 삭제 취소됨")
    except Exception as e:
        db.rollback()
        print(f"\n❌ 삭제 실패: {e}")
    finally:
        db.close()

def delete_by_category(category: str):
    """카테고리별 삭제"""
    db = SessionLocal()
    try:
        # 삭제할 항목 확인
        items = db.query(MapleDictionary).filter_by(category=category).all()
        
        if not items:
            print(f"\n❌ '{category}' 카테고리 항목이 없습니다.")
            return
        
        print("\n" + "="*60)
        print(f"🗑️  '{category}' 카테고리 삭제 대상 ({len(items)}개)")
        print("="*60)
        for idx, item in enumerate(items, 1):
            print(f"{idx}. {item.canonical_name}")
        print("="*60)
        
        # 삭제 확인
        confirm = input(f"\n❓ '{category}' 카테고리 {len(items)}개 항목을 삭제하시겠습니까? (y/N): ").strip()
        if confirm.lower() == 'y':
            deleted_count = db.query(MapleDictionary)\
                .filter_by(category=category)\
                .delete(synchronize_session=False)
            
            db.commit()
            print(f"\n✅ {deleted_count}개 항목 삭제 완료!")
        else:
            print("\n❌ 삭제 취소됨")
    except Exception as e:
        db.rollback()
        print(f"\n❌ 삭제 실패: {e}")
    finally:
        db.close()

def delete_all():
    """전체 데이터 삭제 (주의!)"""
    db = SessionLocal()
    try:
        count = db.query(MapleDictionary).count()
        
        if count == 0:
            print("❌ 삭제할 데이터가 없습니다.")
            return
        
        print(f"⚠️  경고: 전체 {count}개 항목을 삭제합니다!")
        confirm = input("정말로 전체 삭제하시겠습니까? 'DELETE ALL'을 입력하세요: ")
        
        if confirm == 'DELETE ALL':
            deleted_count = db.query(MapleDictionary).delete()
            db.commit()
            print(f"✅ {deleted_count}개 항목 전체 삭제 완료!")
        else:
            print("❌ 삭제 취소됨 (정확히 'DELETE ALL'을 입력해야 합니다)")
    except Exception as e:
        db.rollback()
        print(f"❌ 삭제 실패: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📚 사용법:")
        print("  python delete_data.py <canonical_name>           # 단일 삭제")
        print("  python delete_data.py <canonical_name> --force   # 확인 없이 삭제")
        print("  python delete_data.py --names 헤네시스 페리온    # 여러 개 삭제")
        print("  python delete_data.py --category NPC             # 카테고리별 삭제")
        print("  python delete_data.py --all                      # 전체 삭제 (주의!)")
        sys.exit(1)
    
    # --force 옵션 확인
    force = "--force" in sys.argv
    if force:
        sys.argv.remove("--force")
    
    if sys.argv[1] == "--names":
        # 여러 개 삭제
        names = sys.argv[2:]
        delete_by_names(names)
    elif sys.argv[1] == "--category":
        # 카테고리별 삭제
        if len(sys.argv) < 3:
            print("❌ 카테고리를 입력하세요. (예: MAP, NPC, BOSS)")
            sys.exit(1)
        delete_by_category(sys.argv[2])
    elif sys.argv[1] == "--all":
        # 전체 삭제
        delete_all()
    else:
        # 단일 삭제
        delete_by_name(sys.argv[1], force=force)
