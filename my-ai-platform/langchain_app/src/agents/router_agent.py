"""
Router Agent - Query Intent 분석 및 검색 전략 결정
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import json
import logging

logger = logging.getLogger(__name__)


class QueryIntent(str, Enum):
    """Query 의도 분류"""
    # NPC 관련
    CLASS_CHANGE = "class_change"      # 전직
    NPC_LOCATION = "npc_location"      # NPC 위치
    NPC_SERVICE = "npc_service"        # NPC 서비스
    
    # MAP 관련
    HUNTING_GROUND = "hunting_ground"  # 사냥터
    MAP_LOCATION = "map_location"      # 맵 위치
    MAP_FEATURE = "map_feature"        # 맵 특징
    
    # ITEM 관련
    ITEM_PURCHASE = "item_purchase"    # 아이템 구매
    ITEM_DROP = "item_drop"            # 아이템 드랍
    ITEM_INFO = "item_info"            # 아이템 정보
    
    # MONSTER 관련
    MONSTER_LOCATION = "monster_location"  # 몬스터 위치
    MONSTER_INFO = "monster_info"          # 몬스터 정보
    
    # 관계 관련
    QUEST_RELATION = "quest_relation"  # 퀘스트 연관
    ITEM_RELATION = "item_relation"    # 아이템 연관
    
    # 일반
    GENERAL = "general"                # 일반 질문


class SearchStrategy(str, Enum):
    """검색 전략"""
    SIMPLE = "simple"        # PostgreSQL 직접 검색
    SEMANTIC = "semantic"    # Milvus 의미 검색
    RELATION = "relation"    # Neo4j 관계 검색
    HYBRID = "hybrid"        # 복합 검색


class RouterAgent:
    """
    Query Intent 분석 및 검색 전략 결정
    
    역할:
    1. Query의 의도(Intent) 파악
    2. 검색할 Category 결정
    3. 검색 전략 결정
    4. 핵심 키워드 추출
    """
    
    ROUTER_SYSTEM_PROMPT = """당신은 메이플스토리 검색 시스템의 Router입니다.
사용자의 질문을 분석하여 의도(Intent)와 검색 전략을 결정합니다.

## 주요 Intent 분류

### NPC 관련
- class_change: 전직, 직업 변경 (예: "도적 전직 어디서?", "궁수로 전직하려면?")
- npc_location: NPC 위치 찾기 (예: "다크로드 어디?", "페이슨 위치")
- npc_service: NPC가 제공하는 서비스 (예: "창고 어디?", "상점 찾기")

### MAP 관련
- hunting_ground: 사냥터 찾기 (예: "도적 사냥터 추천", "20레벨 사냥터")
- map_location: 맵 위치 (예: "헤네시스 어떻게 가?", "리스항구 가는 법")
- map_feature: 맵 특징 (예: "엘리니아에 뭐있어?", "커닝시티 특징")

### ITEM 관련
- item_purchase: 아이템 구매 (예: "아이스진 어디서 사?", "물약 파는 곳")
- item_drop: 아이템 드랍 (예: "아이스진 떨구는 몹", "어디서 나와?")
- item_info: 아이템 정보 (예: "아이스진 능력치", "가격은?")

### MONSTER 관련
- monster_location: 몬스터 위치 (예: "스포아 어디?", "주황버섯 사냥터")
- monster_info: 몬스터 정보 (예: "스포아 레벨", "체력은?")

## Category 우선순위

Intent에 따른 Category:
- class_change → NPC (전직관)
- hunting_ground → MAP, MONSTER (사냥터)
- item_purchase → ITEM, NPC (상점)
- item_drop → ITEM, MONSTER (드랍)
- npc_location → NPC, MAP (NPC 위치)
- monster_location → MONSTER, MAP (몬스터 위치)

## 검색 전략

- SIMPLE: 정확한 이름/위치 검색 (PostgreSQL)
- SEMANTIC: 의미 기반 추천/검색 (Milvus)
- RELATION: 관계 기반 검색 (Neo4j)
- HYBRID: 복합 검색

## 응답 형식 (JSON)

{
  "intent": "class_change",
  "categories": ["NPC"],
  "strategy": "SIMPLE",
  "keywords": ["도적", "전직"],
  "reasoning": "도적으로 전직하기 위한 NPC를 찾는 질문"
}"""

    def __init__(
        self,
        llm: Optional[ChatOllama] = None,
        verbose: bool = False
    ):
        self.llm = llm or ChatOllama(
            model="llama3.2:latest",
            temperature=0.0
        )
        self.verbose = verbose
    
    def route(self, query: str) -> Dict[str, Any]:
        """
        Query를 분석하여 검색 전략 결정
        
        Args:
            query: 사용자 질문
            
        Returns:
            {
                "intent": QueryIntent,
                "categories": List[str],
                "strategy": SearchStrategy,
                "keywords": List[str],
                "reasoning": str
            }
        """
        if self.verbose:
            print(f"\n🧭 Router: 분석 중... '{query}'")
        
        try:
            # LLM으로 Intent 분석
            messages = [
                SystemMessage(content=self.ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=f"질문: {query}\n\nJSON 형식으로 분석 결과를 응답해주세요.")
            ]
            
            response = self.llm.invoke(messages)
            
            # JSON 파싱
            result = self._parse_response(response.content)
            
            if self.verbose:
                print(f"   Intent: {result['intent']}")
                print(f"   Categories: {result['categories']}")
                print(f"   Strategy: {result['strategy']}")
                print(f"   Keywords: {result['keywords']}")
                print(f"   Reasoning: {result['reasoning']}")
            
            return result
            
        except Exception as e:
            logger.warning(f"Router LLM 실패, Fallback 사용: {e}")
            # Fallback: 키워드 기반 분류
            return self._fallback_classification(query)
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """LLM 응답을 파싱"""
        try:
            # JSON 블록 추출
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            # JSON 파싱
            data = json.loads(content)
            
            return {
                "intent": data.get("intent", QueryIntent.GENERAL),
                "categories": data.get("categories", []),
                "strategy": data.get("strategy", SearchStrategy.SEMANTIC),
                "keywords": data.get("keywords", []),
                "reasoning": data.get("reasoning", "")
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패: {e}, content={content}")
            # Fallback: 키워드 기반 간단한 분류
            return self._fallback_classification(content)
    
    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """LLM 실패 시 키워드 기반 분류 (정교한 규칙 기반)"""
        query_lower = query.lower()
        
        # 1. 전직 관련 (최우선)
        if any(word in query_lower for word in ["전직", "직업", "배우", "가르쳐"]):
            return {
                "intent": QueryIntent.CLASS_CHANGE,
                "categories": ["NPC"],
                "strategy": SearchStrategy.SIMPLE,
                "keywords": [query],
                "reasoning": "키워드 기반: 전직 - NPC 우선 검색"
            }
        
        # 2. 사냥터 관련 (MAP + MONSTER)
        elif any(word in query_lower for word in ["사냥터", "사냥", "레벨업", "추천"]):
            # "도적 사냥터" 같은 경우
            return {
                "intent": QueryIntent.HUNTING_GROUND,
                "categories": ["MAP", "MONSTER"],
                "strategy": SearchStrategy.SEMANTIC,
                "keywords": [query],
                "reasoning": "키워드 기반: 사냥터 - MAP/MONSTER 우선"
            }
        
        # 3. 아이템 구매
        elif any(word in query_lower for word in ["구매", "사다", "사", "파는", "상점"]):
            return {
                "intent": QueryIntent.ITEM_PURCHASE,
                "categories": ["ITEM", "NPC"],
                "strategy": SearchStrategy.SIMPLE,
                "keywords": [query],
                "reasoning": "키워드 기반: 구매 - ITEM/NPC"
            }
        
        # 4. 아이템 드랍
        elif any(word in query_lower for word in ["드랍", "떨구", "떨어", "나와"]):
            return {
                "intent": QueryIntent.ITEM_DROP,
                "categories": ["ITEM", "MONSTER"],
                "strategy": SearchStrategy.SIMPLE,
                "keywords": [query],
                "reasoning": "키워드 기반: 드랍 - ITEM/MONSTER"
            }
        
        # 5. 몬스터 위치
        elif any(word in query_lower for word in ["잡", "몬스터", "몹"]):
            return {
                "intent": QueryIntent.MONSTER_LOCATION,
                "categories": ["MONSTER", "MAP"],
                "strategy": SearchStrategy.SIMPLE,
                "keywords": [query],
                "reasoning": "키워드 기반: 몬스터 - MONSTER/MAP"
            }
        
        # 6. NPC 위치
        elif any(word in query_lower for word in ["어디", "위치", "있어"]):
            # 이름이 있으면 NPC 우선
            return {
                "intent": QueryIntent.NPC_LOCATION,
                "categories": ["NPC", "MAP"],
                "strategy": SearchStrategy.SIMPLE,
                "keywords": [query],
                "reasoning": "키워드 기반: 위치 - NPC/MAP 검색"
            }
        
        # 7. 맵 이동
        elif any(word in query_lower for word in ["가는", "이동", "가려면"]):
            return {
                "intent": QueryIntent.MAP_LOCATION,
                "categories": ["MAP"],
                "strategy": SearchStrategy.SIMPLE,
                "keywords": [query],
                "reasoning": "키워드 기반: 이동 - MAP"
            }
        
        # 8. 일반 질문 (의미 검색)
        else:
            return {
                "intent": QueryIntent.GENERAL,
                "categories": [],
                "strategy": SearchStrategy.SEMANTIC,
                "keywords": [query],
                "reasoning": "키워드 기반: 일반 - 의미 검색"
            }


# 편의 함수
def route_query(query: str, verbose: bool = False) -> Dict[str, Any]:
    """간단한 Router 실행"""
    router = RouterAgent(verbose=verbose)
    return router.route(query)
