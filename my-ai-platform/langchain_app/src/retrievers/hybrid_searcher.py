"""
Hybrid Search with Intent-based Routing
Router Agent → Category 우선순위 결정 → PostgreSQL/Milvus 검색
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from src.retrievers.db_searcher import MapleDBSearcher
from src.retrievers.milvus_retriever import MilvusRetriever
from src.agents.router_agent import RouterAgent

logger = logging.getLogger(__name__)


class HybridSearcher:
    """
    Intent 기반 하이브리드 검색
    
    전략:
    1. Router Agent로 Intent 분석
       - Query의 의도 파악
       - 검색할 Category 결정
    
    2. Category 우선순위 적용
       - Intent에 맞는 Category 우선 검색
       - 예: "전직" → NPC 우선, "사냥터" → MAP/MONSTER 우선
    
    3. PostgreSQL + Milvus 통합 검색
       - PostgreSQL: 정확한 매칭
       - Milvus: 의미 기반 검색
    """
    
    def __init__(
        self, 
        db: Session,
        use_milvus: bool = True,
        use_router: bool = True,
        verbose: bool = False
    ):
        self.db = db
        self.use_milvus = use_milvus
        self.use_router = use_router
        self.verbose = verbose
        
        # PostgreSQL Searcher
        self.pg_searcher = MapleDBSearcher(db)
        
        # Milvus Searcher (옵션)
        self.milvus_searcher = None
        if use_milvus:
            try:
                self.milvus_searcher = MilvusRetriever()
                logger.info("✅ Milvus 검색 활성화")
            except Exception as e:
                logger.warning(f"⚠️ Milvus 연결 실패, PostgreSQL만 사용: {e}")
                self.use_milvus = False
        
        # Router Agent (옵션)
        self.router = None
        if use_router:
            try:
                self.router = RouterAgent(verbose=False)
                logger.info("✅ Router Agent 활성화")
            except Exception as e:
                logger.warning(f"⚠️ Router Agent 초기화 실패: {e}")
                self.use_router = False
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        pg_threshold: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Intent 기반 하이브리드 검색
        
        Args:
            query: 검색 쿼리
            category: 카테고리 필터 (옵션, Router가 자동 결정)
            limit: 최대 결과 개수
            pg_threshold: PostgreSQL 결과가 이 개수 이상이면 확장, 미만이면 폴백
            
        Returns:
            검색 결과 리스트 (점수 순 정렬)
        """
        if self.verbose:
            print(f"\n🔍 Hybrid Search: '{query}'")
        
        # Step 0: Router Agent로 Intent 분석
        router_result = None
        if self.use_router and self.router and not category:
            try:
                router_result = self.router.route(query)
                if self.verbose:
                    print(f"   🧭 Intent: {router_result['intent']}")
                    print(f"   📁 Categories: {router_result['categories']}")
                
                # Router가 제안한 첫 번째 category 사용
                if router_result['categories']:
                    category = router_result['categories'][0]
                    if self.verbose:
                        print(f"   ✅ Category 선택: {category}")
            except Exception as e:
                logger.warning(f"Router 실패, category 없이 진행: {e}")
        
        # Step 1: PostgreSQL 검색
        pg_results = self._postgres_search(query, category, limit)
        
        if self.verbose:
            print(f"   PostgreSQL: {len(pg_results)}개 결과")
        
        # Milvus 사용 안하면 PostgreSQL 결과만 반환
        if not self.use_milvus or not self.milvus_searcher:
            return pg_results[:limit]
        
        # Step 2: 결과 분기
        if len(pg_results) >= pg_threshold:
            # ✅ 충분히 찾음 → Milvus로 연관 확장
            if self.verbose:
                print(f"   ✅ PostgreSQL 성공 → Milvus 연관 검색")
            
            milvus_results = self._milvus_expansion_search(pg_results, limit)
            
            if self.verbose:
                print(f"   Milvus 확장: {len(milvus_results)}개 추가")
            
            # 병합 & 랭킹
            merged = self._merge_results(pg_results, milvus_results, mode="expansion")
            
        else:
            # ⚠️ 부족함 → Milvus로 의미 검색 (폴백)
            if self.verbose:
                print(f"   ⚠️ PostgreSQL 부족 ({len(pg_results)}/{pg_threshold}) → Milvus 의미 검색")
            
            milvus_results = self._milvus_semantic_search(query, limit)
            
            if self.verbose:
                print(f"   Milvus 의미: {len(milvus_results)}개 결과")
            
            # 병합 & 랭킹
            merged = self._merge_results(pg_results, milvus_results, mode="fallback")
        
        # 최종 결과
        final_results = merged[:limit]
        
        if self.verbose:
            print(f"   📊 최종: {len(final_results)}개\n")
        
        return final_results
    
    def _postgres_search(
        self,
        query: str,
        category: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """PostgreSQL 검색 (빠른 정확 매칭)"""
        try:
            results = self.pg_searcher.search(query, category=category, limit=limit)
            return results
        except Exception as e:
            logger.error(f"PostgreSQL 검색 실패: {e}")
            return []
    
    def _milvus_expansion_search(
        self,
        pg_results: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Milvus 연관 확장 검색
        PostgreSQL에서 찾은 엔티티들의 연관 항목 검색
        """
        if not self.milvus_searcher:
            return []
        
        milvus_results = []
        seen_ids = set()
        
        # PostgreSQL에서 찾은 TOP 3 엔티티로 확장
        for pg_item in pg_results[:3]:
            data = pg_item.get("data", {})
            canonical_name = data.get("canonical_name", "")
            item_id = data.get("id")
            
            if item_id:
                seen_ids.add(str(item_id))
            
            if not canonical_name:
                continue
            
            try:
                # canonical_name으로 Milvus 검색
                results = self.milvus_searcher.search(canonical_name, top_k=5)
                
                # 결과 추가
                for result in results:
                    result_id = result.get("id")
                    
                    if result_id and result_id not in seen_ids:
                        milvus_results.append({
                            "score": result.get("score", 0) * 50,  # 점수 조정
                            "match_type": "milvus_expansion",
                            "data": result,
                            "source_entity": canonical_name
                        })
                        seen_ids.add(result_id)
                        
                        if len(milvus_results) >= limit:
                            break
                
            except Exception as e:
                logger.warning(f"Milvus 확장 검색 실패 ({canonical_name}): {e}")
                continue
            
            if len(milvus_results) >= limit:
                break
        
        return milvus_results
    
    def _milvus_semantic_search(
        self,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Milvus 의미 검색 (폴백)
        질문 전체를 의미적으로 검색
        """
        if not self.milvus_searcher:
            return []
        
        try:
            # Milvus Q&A 검색
            results = self.milvus_searcher.search(query, top_k=limit)
            
            # 결과 포맷팅
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "score": result.get("score", 0) * 100,  # 점수 조정
                    "match_type": "milvus_semantic",
                    "data": result
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Milvus 의미 검색 실패: {e}")
            return []
    
    def _merge_results(
        self,
        pg_results: List[Dict[str, Any]],
        milvus_results: List[Dict[str, Any]],
        mode: str = "expansion"
    ) -> List[Dict[str, Any]]:
        """
        PostgreSQL + Milvus 결과 병합
        
        Args:
            mode: "expansion" (확장) 또는 "fallback" (폴백)
        """
        merged = {}
        
        # PostgreSQL 결과 추가 (높은 가중치)
        pg_weight = 1.5 if mode == "expansion" else 1.0
        
        for item in pg_results:
            data = item.get("data", {})
            item_id = data.get("id")
            
            if not item_id:
                continue
            
            merged[str(item_id)] = {
                "score": item.get("score", 0) * pg_weight,
                "match_type": item.get("match_type", "postgres"),
                "data": data,
                "sources": ["postgres"]
            }
        
        # Milvus 결과 추가
        milvus_weight = 0.8 if mode == "expansion" else 1.2
        
        for item in milvus_results:
            data = item.get("data", {})
            item_id = data.get("id")
            
            if not item_id:
                continue
            
            item_id_str = str(item_id)
            score = item.get("score", 0) * milvus_weight
            
            if item_id_str in merged:
                # 이미 있으면 점수 합산 (양쪽에서 찾은 것!)
                merged[item_id_str]["score"] += score
                merged[item_id_str]["sources"].append("milvus")
                merged[item_id_str]["match_type"] = "both"
            else:
                # 새로운 항목
                merged[item_id_str] = {
                    "score": score,
                    "match_type": item.get("match_type", "milvus"),
                    "data": data,
                    "sources": ["milvus"]
                }
        
        # 점수 순 정렬
        sorted_results = sorted(
            merged.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return sorted_results


# 편의 함수
def hybrid_search(
    db: Session,
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
    use_milvus: bool = True
) -> List[Dict[str, Any]]:
    """
    간단한 하이브리드 검색 함수
    
    Usage:
        results = hybrid_search(db, "아이스진 어디서 사나요?")
    """
    searcher = HybridSearcher(db, use_milvus=use_milvus)
    return searcher.search(query, category=category, limit=limit)
