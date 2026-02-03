#!/usr/bin/env python3
"""
maple_data.json 정규화
- Category별로 데이터 구조 통일
- 표준 스키마에 맞춰서 모든 필드 정리
- 값이 없으면 null 처리
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import defaultdict

# 경로 설정
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "training/data/input_data/maple_data.json"
OUTPUT_FILE = PROJECT_ROOT / "training/data/input_data/maple_data_normalized.json"
BACKUP_FILE = PROJECT_ROOT / "training/data/input_data/maple_data.backup.json"


# Category별 표준 스키마 정의
STANDARD_SCHEMAS = {
    "MAP": {
        # 기본 필드
        "category": "MAP",
        "map_type": None,
        "region": None,
        "bgm": None,
        "description": None,
        
        # 연결 정보
        "adjacent_maps": [],
        "special_portals": [],
        
        # 거주자
        "resident_npcs": [],
        "resident_monsters": [],
        
        # 기능/특징
        "features": [],
        
        # 레벨 정보
        "min_level": 0,  # 기본값: 0
        "recommended_level_range": None,
        
        # 안전 지대
        "is_safe_zone": True,  # 기본값: True
        
        # 기타
        "required_quest": None,
        "star_force_limit": 0,  # 기본값: 0
        "arcane_power_limit": 0,  # 기본값: 0
    },
    
    "ITEM": {
        # 기본 필드
        "category": "ITEM",
        "item_type": None,
        "description": None,
        
        # 가격/구매
        "price": None,
        "obtainable_from": [],
        
        # 요구 사항
        "required_level": 0,  # 기본값: 0
        "required_job": [],  # 기본값: 빈 리스트
        "required_stats": None,
        
        # 능력치
        "stats": None,
        "effects": [],
        
        # 특성
        "tradable": None,
        "stackable": None,
        "max_stack": None,
        
        # 기타
        "quest_item": None,
        "consumable": None,
    },
    
    "NPC": {
        # 기본 필드
        "category": "NPC",
        "npc_type": None,
        "description": None,
        
        # 위치
        "location": None,
        "region": None,
        
        # 서비스
        "services": [],
        "sells_items": [],
        
        # 퀘스트
        "related_quests": [],
        
        # 대화
        "dialogue": None,
        
        # 기타
        "is_merchant": None,
        "is_quest_giver": None,
    },
    
    "MONSTER": {
        # 기본 필드
        "category": "MONSTER",
        "monster_type": "NORMAL",  # 기본값: NORMAL
        "description": None,
        
        # 스탯
        "level": None,
        "hp": None,
        "mp": None,
        "exp": None,
        "attack": None,
        "defense": None,
        
        # 위치
        "spawn_maps": [],
        "region": None,
        
        # 드랍
        "drops": [],
        "meso_drop_range": None,
        
        # 속성
        "element": None,
        "boss": None,
        
        # 특징
        "abilities": [],
        "weaknesses": [],
        
        # 기타
        "respawn_time": None,
    }
}


def collect_all_fields_by_category(data: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
    """각 category별로 사용된 모든 필드 수집"""
    fields_by_category = defaultdict(set)
    
    for item in data:
        category = item.get('category')
        if category:
            detail_data = item.get('detail_data', {})
            if isinstance(detail_data, dict):
                for key in detail_data.keys():
                    fields_by_category[category].add(key)
    
    return fields_by_category


def normalize_entity(entity: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    엔티티를 표준 스키마에 맞춰서 정규화
    
    Args:
        entity: 원본 엔티티
        schema: 표준 스키마
        
    Returns:
        정규화된 detail_data
    """
    detail_data = entity.get('detail_data', {})
    if not isinstance(detail_data, dict):
        detail_data = {}
    
    # 표준 스키마로 새로운 객체 생성
    normalized = {}
    
    for key, default_value in schema.items():
        # 기존 값이 있고 None이 아닌 경우에만 사용
        if key in detail_data and detail_data[key] is not None:
            normalized[key] = detail_data[key]
        else:
            # 기본값 사용
            normalized[key] = default_value
    
    return normalized


def normalize_data(input_file: Path, output_file: Path) -> None:
    """데이터 정규화 메인 함수"""
    
    print("=" * 80)
    print("maple_data.json 정규화 시작")
    print("=" * 80)
    print()
    
    # 1. 원본 파일 읽기
    print(f"📖 원본 파일 읽기: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   총 {len(data)}개 엔티티")
    
    # 2. Category별 통계
    category_counts = defaultdict(int)
    for item in data:
        category = item.get('category')
        category_counts[category] += 1
    
    print(f"\n📊 Category별 엔티티 수:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count}개")
    
    # 3. 현재 사용 중인 필드 수집
    print(f"\n🔍 현재 사용 중인 필드 분석...")
    fields_by_category = collect_all_fields_by_category(data)
    
    for category, fields in sorted(fields_by_category.items()):
        print(f"\n   [{category}] 사용 중인 필드 ({len(fields)}개):")
        for field in sorted(fields):
            print(f"      - {field}")
    
    # 4. 정규화 수행
    print(f"\n🔨 정규화 수행 중...")
    normalized_data = []
    
    for entity in data:
        category = entity.get('category')
        
        if category in STANDARD_SCHEMAS:
            # 표준 스키마 적용
            schema = STANDARD_SCHEMAS[category]
            normalized_detail = normalize_entity(entity, schema)
            
            # 새로운 엔티티 생성
            normalized_entity = {
                "canonical_name": entity.get('canonical_name'),
                "category": category,
                "synonyms": entity.get('synonyms', []),
                "description": entity.get('description', ''),
                "detail_data": normalized_detail
            }
            
            normalized_data.append(normalized_entity)
        else:
            # 스키마가 없는 category는 그대로 유지
            print(f"   ⚠️  스키마 없음: {category}")
            normalized_data.append(entity)
    
    print(f"   ✅ {len(normalized_data)}개 엔티티 정규화 완료")
    
    # 5. 백업 생성
    print(f"\n💾 원본 백업: {BACKUP_FILE}")
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 6. 정규화된 데이터 저장
    print(f"\n💾 정규화된 데이터 저장: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_data, f, ensure_ascii=False, indent=2)
    
    # 7. 검증
    print(f"\n✅ 정규화 완료!")
    print(f"\n📊 결과:")
    print(f"   원본: {len(data)}개")
    print(f"   정규화: {len(normalized_data)}개")
    print(f"   백업: {BACKUP_FILE}")
    print(f"   출력: {output_file}")
    
    print("\n" + "=" * 80)
    print("정규화 완료! 🎉")
    print("=" * 80)
    print()
    print("다음 단계:")
    print("1. maple_data_normalized.json 확인")
    print("2. 문제 없으면 원본 교체:")
    print(f"   mv {output_file} {input_file}")
    print("3. PostgreSQL 재생성:")
    print("   docker exec -it ai-langchain-api python /app/scripts/import_data.py --drop")
    print("4. Milvus 재생성:")
    print("   echo 'y' | docker exec -i ai-langchain-api python /app/scripts/sync_to_milvus.py --drop")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="maple_data.json 정규화")
    parser.add_argument("--input", type=str, default=str(INPUT_FILE), help="입력 파일")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FILE), help="출력 파일")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ 파일이 없습니다: {input_path}")
        exit(1)
    
    try:
        normalize_data(input_path, output_path)
    except Exception as e:
        print(f"\n❌ 정규화 실패: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
