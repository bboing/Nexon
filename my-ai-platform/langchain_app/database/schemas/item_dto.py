from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from enum import Enum

class ItemType(str, Enum):
    """아이템 종류"""
    WEAPON = "WEAPON"           # 무기
    ARMOR = "ARMOR"             # 방어구
    EQUIPMENT = "EQUIPMENT"     # 장비 (무기/방어구 통칭)
    ACCESSORY = "ACCESSORY"     # 악세서리
    CONSUMABLE = "CONSUMABLE"   # 소비 아이템
    ETC = "ETC"                 # 기타
    QUEST = "QUEST"             # 퀘스트 아이템
    CASH = "CASH"               # 캐시 아이템

class ItemGrade(str, Enum):
    """아이템 등급"""
    COMMON = "COMMON"           # 일반
    RARE = "RARE"               # 레어
    EPIC = "EPIC"               # 에픽
    UNIQUE = "UNIQUE"           # 유니크
    LEGENDARY = "LEGENDARY"     # 레전더리

class ItemMetadata(BaseModel):
    """
    메이플스토리 아이템 메타데이터 (MapleDictionary.detail_data용)
    """
    category: Literal["ITEM"] = "ITEM"
    
    # 1. 기본 정보
    item_type: ItemType = Field(..., description="아이템 종류")
    grade: Optional[ItemGrade] = Field(None, description="아이템 등급")
    description: Optional[str] = Field(None, description="아이템 설명")
    
    # 2. 획득 정보
    obtainable_from: List[str] = Field(default_factory=list, description="획득처 (몬스터, NPC, 퀘스트 등)")
    drop_rate: Optional[float] = Field(None, description="드랍률 (0.0~1.0)")
    
    # 3. 판매 정보
    npc_price: Optional[int] = Field(None, description="NPC 판매 가격")
    sell_price: Optional[int] = Field(None, description="NPC 판매 시 가격")
    tradeable: bool = Field(True, description="거래 가능 여부")
    
    # 4. 스탯 정보 (무기/방어구의 경우)
    stats: Optional[Dict[str, int]] = Field(None, description="스탯 정보 (공격력, 방어력 등)")
    required_level: int = Field(0, description="착용 가능 레벨")
    required_job: List[str] = Field(default_factory=list, description="착용 가능 직업")
    
    # 5. 효과 (소비 아이템의 경우)
    effects: List[Dict[str, Any]] = Field(default_factory=list, description="아이템 효과")
    
    # 6. 관계 정보
    related_items: List[str] = Field(default_factory=list, description="관련 아이템 (세트, 재료 등)")
    related_quests: List[str] = Field(default_factory=list, description="관련 퀘스트")
    
    def extract_graph_relations(self, item_name: str) -> List[Dict[str, Any]]:
        """
        Neo4j 연동을 위한 관계 데이터 추출
        """
        relations = []
        
        # 아이템-몬스터 드랍 관계
        for source in self.obtainable_from:
            if "몬스터:" in source or any(keyword in source for keyword in ["버섯", "슬라임", "좀비"]):
                relations.append({
                    "from_node": {"label": "Monster", "name": source.replace("몬스터:", "").strip()},
                    "to_node": {"label": "Item", "name": item_name},
                    "relation": "DROPS",
                    "properties": {"drop_rate": self.drop_rate} if self.drop_rate else {}
                })
        
        # 아이템-퀘스트 관계
        for quest in self.related_quests:
            relations.append({
                "from_node": {"label": "Quest", "name": quest},
                "to_node": {"label": "Item", "name": item_name},
                "relation": "REWARDS"
            })
        
        # 아이템-아이템 관계 (세트, 재료)
        for related_item in self.related_items:
            relations.append({
                "from_node": {"label": "Item", "name": item_name},
                "to_node": {"label": "Item", "name": related_item},
                "relation": "RELATED_TO"
            })
        
        return relations
