"""
MapleDB Searcher
PostgreSQL maple_dictionary 테이블에서 키워드 기반 검색
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, Text
from database.models.maple_dictionary import MapleDictionary, CategoryEnum
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class MapleDBSearcher:
    """
    메이플 용어 사전 검색기
    
    검색 우선순위:
    1. canonical_name 정확 매칭 (가장 높은 점수)
    2. synonyms 배열 검색 (높은 점수)
    3. description 포함 검색 (중간 점수)
    4. detail_data JSONB 검색 (낮은 점수)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def search(
        self, 
        keyword: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        키워드로 maple_dictionary 검색
        
        Args:
            keyword: 검색 키워드
            category: 카테고리 필터 (MAP, NPC, ITEM, MONSTER 등)
            limit: 최대 결과 개수
            
        Returns:
            검색 결과 리스트 (점수 순 정렬)
        """
        if not keyword or not keyword.strip():
            logger.warning("Empty keyword provided")
            return []
        
        keyword = keyword.strip()
        logger.info(f"🔍 검색 키워드: '{keyword}', 카테고리: {category or '전체'}")
        
        results = []
        
        # 1. Exact match on canonical_name (Score: 100)
        exact_matches = self._search_exact(keyword, category)
        for item in exact_matches:
            results.append({
                "score": 100,
                "match_type": "exact_name",
                "data": item.to_dict()
            })
        
        # 2. Synonyms array search (Score: 90)
        synonym_matches = self._search_synonyms(keyword, category, exclude_ids=[r["data"]["id"] for r in results])
        for item in synonym_matches:
            results.append({
                "score": 90,
                "match_type": "synonym",
                "data": item.to_dict()
            })
        
        # 3. Description contains (Score: 70)
        description_matches = self._search_description(keyword, category, exclude_ids=[r["data"]["id"] for r in results])
        for item in description_matches:
            results.append({
                "score": 70,
                "match_type": "description",
                "data": item.to_dict()
            })
        
        # 4. JSONB detail_data search (Score: 50)
        detail_matches = self._search_detail_data(keyword, category, exclude_ids=[r["data"]["id"] for r in results])
        for item in detail_matches:
            results.append({
                "score": 50,
                "match_type": "detail_data",
                "data": item.to_dict()
            })
        
        # 점수 순 정렬 및 제한
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:limit]
        
        logger.info(f"✅ 검색 완료: {len(results)}개 결과")
        return results
    
    def _search_exact(
        self, 
        keyword: str, 
        category: Optional[str] = None
    ) -> List[MapleDictionary]:
        """canonical_name 정확 매칭"""
        query = self.db.query(MapleDictionary).filter(
            MapleDictionary.canonical_name == keyword
        )
        
        if category:
            query = query.filter(MapleDictionary.category == category)
        
        return query.all()
    
    def _search_synonyms(
        self, 
        keyword: str, 
        category: Optional[str] = None,
        exclude_ids: List[str] = None
    ) -> List[MapleDictionary]:
        """synonyms 배열 검색"""
        query = self.db.query(MapleDictionary).filter(
            MapleDictionary.synonyms.contains([keyword])  # PostgreSQL ARRAY contains
        )
        
        if category:
            query = query.filter(MapleDictionary.category == category)
        
        if exclude_ids:
            query = query.filter(~MapleDictionary.id.in_(exclude_ids))
        
        return query.all()
    
    def _search_description(
        self, 
        keyword: str, 
        category: Optional[str] = None,
        exclude_ids: List[str] = None
    ) -> List[MapleDictionary]:
        """description 포함 검색 (ILIKE)"""
        query = self.db.query(MapleDictionary).filter(
            MapleDictionary.description.ilike(f"%{keyword}%")
        )
        
        if category:
            query = query.filter(MapleDictionary.category == category)
        
        if exclude_ids:
            query = query.filter(~MapleDictionary.id.in_(exclude_ids))
        
        return query.limit(5).all()  # description 검색은 최대 5개
    
    def _search_detail_data(
        self, 
        keyword: str, 
        category: Optional[str] = None,
        exclude_ids: List[str] = None
    ) -> List[MapleDictionary]:
        """JSONB detail_data 검색"""
        # PostgreSQL JSONB 텍스트 검색
        query = self.db.query(MapleDictionary).filter(
            func.cast(MapleDictionary.detail_data, Text).ilike(f"%{keyword}%")
        )
        
        if category:
            query = query.filter(MapleDictionary.category == category)
        
        if exclude_ids:
            query = query.filter(~MapleDictionary.id.in_(exclude_ids))
        
        return query.limit(3).all()  # JSONB 검색은 최대 3개
    
    def search_by_category_and_field(
        self,
        category: str,
        field_name: str,
        field_value: Any
    ) -> List[Dict[str, Any]]:
        """
        특정 카테고리의 detail_data 내 필드로 검색
        
        예시:
        - category="ITEM", field_name="item_type", field_value="WEAPON"
        - category="MONSTER", field_name="level", field_value=10
        """
        query = self.db.query(MapleDictionary).filter(
            and_(
                MapleDictionary.category == category,
                MapleDictionary.detail_data[field_name].astext == str(field_value)
            )
        )
        
        results = query.all()
        logger.info(f"🔍 필드 검색 ({category}.{field_name}={field_value}): {len(results)}개")
        
        return [
            {
                "score": 80,
                "match_type": f"field_{field_name}",
                "data": item.to_dict()
            }
            for item in results
        ]
    
    def get_related_entities(
        self, 
        canonical_name: str
    ) -> Dict[str, List[Dict]]:
        """
        특정 엔티티와 연관된 다른 엔티티들 검색
        
        예시: "아이스진" 검색 → 판매 NPC, 드랍하는 몬스터 등
        """
        # 먼저 해당 엔티티 찾기
        entity = self.db.query(MapleDictionary).filter_by(
            canonical_name=canonical_name
        ).first()
        
        if not entity:
            logger.warning(f"Entity not found: {canonical_name}")
            return {}
        
        related = {
            "source": entity.to_dict(),
            "related_npcs": [],
            "related_items": [],
            "related_maps": [],
            "related_monsters": []
        }
        
        detail = entity.detail_data or {}
        
        # detail_data에서 연관 엔티티 추출
        if entity.category == CategoryEnum.ITEM:
            # 아이템의 경우: 판매 NPC, 드랍 몬스터
            obtainable = detail.get("obtainable_from", [])
            for source in obtainable:
                # NPC 검색
                npc_results = self.search(source, category="NPC", limit=1)
                if npc_results:
                    related["related_npcs"].extend(npc_results)
                
                # 몬스터 검색
                monster_results = self.search(source, category="MONSTER", limit=1)
                if monster_results:
                    related["related_monsters"].extend(monster_results)
        
        elif entity.category == CategoryEnum.MONSTER:
            # 몬스터의 경우: 드랍 아이템, 스폰 맵
            drops = detail.get("drops", [])
            for drop in drops:
                item_name = drop.get("item_name")
                if item_name:
                    item_results = self.search(item_name, category="ITEM", limit=1)
                    related["related_items"].extend(item_results)
            
            spawn_maps = detail.get("spawn_maps", [])
            for map_name in spawn_maps:
                map_results = self.search(map_name, category="MAP", limit=1)
                related["related_maps"].extend(map_results)
        
        elif entity.category == CategoryEnum.MAP:
            # 맵의 경우: 거주 NPC, 스폰 몬스터
            resident_npcs = detail.get("resident_npcs", [])
            for npc_name in resident_npcs:
                npc_results = self.search(npc_name, category="NPC", limit=1)
                related["related_npcs"].extend(npc_results)
            
            resident_monsters = detail.get("resident_monsters", [])
            for monster_name in resident_monsters:
                monster_results = self.search(monster_name, category="MONSTER", limit=1)
                related["related_monsters"].extend(monster_results)
        
        logger.info(f"🔗 연관 검색: {canonical_name} → {sum(len(v) for k, v in related.items() if k != 'source')}개")
        return related


# 편의 함수
def search_maple_db(
    db: Session,
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    간단한 검색 함수 (Dependency Injection 용)
    
    Usage in FastAPI:
        @app.get("/search")
        def search(keyword: str, db: Session = Depends(get_db)):
            return search_maple_db(db, keyword)
    """
    searcher = MapleDBSearcher(db)
    return searcher.search(keyword, category, limit)
