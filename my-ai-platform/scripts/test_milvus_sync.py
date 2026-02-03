#!/usr/bin/env python3
"""
Milvus 동기화 테스트
1. Q&A 생성 테스트
2. 임베딩 테스트
3. Milvus 저장 테스트
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

from database.session import SessionLocal
from database.models.maple_dictionary import MapleDictionary
from src.utils.qa_generator import QAGenerator


def test_qa_generation():
    """Q&A 생성 테스트 (DB 읽어서 Q&A 생성)"""
    print("\n" + "="*80)
    print("🧪 Q&A 생성 테스트")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # 샘플 데이터 읽기 (3개만)
        entities = db.query(MapleDictionary).limit(3).all()
        print(f"\n✅ {len(entities)}개 엔티티 로드\n")
        
        # Q&A 생성
        generator = QAGenerator()
        
        for entity in entities:
            entity_dict = entity.to_dict()
            qa_pairs = generator.generate_qa_pairs(entity_dict)
            
            print(f"📌 {entity_dict['canonical_name']} ({entity_dict['category']})")
            print(f"   생성된 Q&A: {len(qa_pairs)}개\n")
            
            for idx, qa in enumerate(qa_pairs, 1):
                print(f"   {idx}. Q: {qa['question']}")
                print(f"      A: {qa['answer'][:80]}...")
                print(f"      타입: {qa['qa_type']}")
                print()
            
            print("-" * 80 + "\n")
        
        print("✅ Q&A 생성 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_embedding_text():
    """임베딩 텍스트 포맷 테스트"""
    print("\n" + "="*80)
    print("🧪 임베딩 텍스트 포맷 테스트")
    print("="*80 + "\n")
    
    generator = QAGenerator()
    
    # 샘플 Q&A
    qa = {
        "question": "아이스진은 어디서 구매할 수 있나요?",
        "answer": "아이스진은 리스항구의 페이슨 NPC에게서 구매할 수 있습니다."
    }
    
    embedding_text = generator.create_embedding_text(qa)
    
    print("Q&A:")
    print(f"  Q: {qa['question']}")
    print(f"  A: {qa['answer']}")
    print()
    print("임베딩 텍스트:")
    print(f"  {embedding_text}")
    print()
    print(f"✅ 총 길이: {len(embedding_text)}자")
    print("✅ 포맷 테스트 완료!")


def test_full_generation():
    """전체 통계 (모든 엔티티)"""
    print("\n" + "="*80)
    print("🧪 전체 Q&A 생성 통계")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    try:
        # 모든 엔티티
        entities = db.query(MapleDictionary).all()
        print(f"✅ {len(entities)}개 엔티티 로드")
        
        # 배치 생성
        generator = QAGenerator()
        entities_dict = [e.to_dict() for e in entities]
        all_qa = generator.generate_batch(entities_dict)
        
        print(f"✅ {len(all_qa)}개 Q&A 생성")
        print(f"📊 평균: {len(all_qa)/len(entities):.1f}개 Q&A/엔티티\n")
        
        # 카테고리별 통계
        from collections import Counter
        
        type_counts = Counter(qa['entity_type'] for qa in all_qa)
        print("카테고리별 Q&A:")
        for entity_type, count in type_counts.items():
            print(f"  {entity_type}: {count}개")
        
        print()
        qa_type_counts = Counter(qa['qa_type'] for qa in all_qa)
        print("Q&A 타입별 (TOP 10):")
        for qa_type, count in sorted(qa_type_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {qa_type}: {count}개")
        
        print("\n✅ 통계 생성 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "qa":
            test_qa_generation()
        elif test_type == "embed":
            test_embedding_text()
        elif test_type == "stat":
            test_full_generation()
        else:
            print("❌ 잘못된 테스트 타입")
            print("사용법: python test_milvus_sync.py [qa|embed|stat]")
    else:
        # 모두 실행
        test_qa_generation()
        test_embedding_text()
        test_full_generation()
