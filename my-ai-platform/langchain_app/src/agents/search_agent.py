"""
ReAct Search Agent
Thought-Action-Observation 루프로 DB를 반복 검색하는 Agent
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
import json
import logging

from src.retrievers.db_searcher import MapleDBSearcher
from src.retrievers.hybrid_searcher import HybridSearcher

logger = logging.getLogger(__name__)


class SearchAgent:
    """
    ReAct 패턴 기반 검색 Agent
    
    사용자 질문 → [Thought → Action → Observation] × N → Final Answer
    """
    
    def __init__(
        self,
        db: Session,
        llm: ChatOllama,
        max_iterations: int = 5,
        verbose: bool = True,
        use_hybrid: bool = True  # Hybrid Search 사용 여부
    ):
        self.db = db
        self.llm = llm
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.conversation_history = []
        
        # Hybrid Search 또는 기본 DB Search
        if use_hybrid:
            try:
                self.searcher = HybridSearcher(db, use_milvus=True, verbose=verbose)
                logger.info("🚀 Hybrid Search (PostgreSQL + Milvus) 활성화")
            except Exception as e:
                logger.warning(f"⚠️ Hybrid Search 실패, 기본 검색 사용: {e}")
                self.searcher = MapleDBSearcher(db)
        else:
            self.searcher = MapleDBSearcher(db)
    
    def run(self, user_question: str) -> Dict[str, Any]:
        """
        Agent 실행
        
        Returns:
            {
                "answer": "최종 답변",
                "thoughts": ["생각1", "생각2", ...],
                "actions": [{"action": "search", "query": "...", "results": [...]}, ...],
                "iterations": 3
            }
        """
        logger.info(f"🤖 Agent 시작: '{user_question}'")
        
        self.conversation_history = []
        thoughts = []
        actions = []
        
        # 시스템 프롬프트
        system_prompt = self._get_system_prompt()
        self.conversation_history.append(SystemMessage(content=system_prompt))
        
        # 사용자 질문
        self.conversation_history.append(HumanMessage(content=user_question))
        
        for iteration in range(self.max_iterations):
            if self.verbose:
                print(f"\n{'='*80}")
                print(f"🔄 Iteration {iteration + 1}/{self.max_iterations}")
                print(f"{'='*80}")
            
            # LLM에게 다음 행동 물어보기
            response = self.llm.invoke(self.conversation_history)
            response_text = response.content
            
            if self.verbose:
                print(f"\n🤔 LLM Response:\n{response_text}\n")
            
            # 응답 파싱
            parsed = self._parse_response(response_text)
            
            # 디버그 로그
            if self.verbose:
                print(f"🔧 Parsed Type: {parsed['type']}")
                if parsed['type'] == 'ACTION':
                    print(f"   Query: {parsed.get('query')}, Category: {parsed.get('category')}")
            
            if parsed["type"] == "FINAL_ANSWER":
                # 최종 답변
                if self.verbose:
                    print(f"✅ 최종 답변 생성 완료!")
                
                return {
                    "answer": parsed["content"],
                    "thoughts": thoughts,
                    "actions": actions,
                    "iterations": iteration + 1,
                    "success": True
                }
            
            elif parsed["type"] == "THOUGHT":
                # 생각만 있는 경우 (드물음)
                thoughts.append(parsed["content"])
                if self.verbose:
                    print(f"💭 Thought: {parsed['content']}")
                # 대화 이어가기
                self.conversation_history.append(AIMessage(content=response_text))
                self.conversation_history.append(HumanMessage(
                    content="생각만 하지 말고 ACTION을 실행하세요."
                ))
            
            elif parsed["type"] == "ACTION":
                # 생각 기록 (ACTION에 포함된 THOUGHT)
                thought = parsed.get("thought", "")
                if thought:
                    thoughts.append(thought)
                    if self.verbose:
                        print(f"💭 Thought: {thought}")
                
                # 행동 실행 (DB 검색)
                action_type = parsed.get("action_type", "search")
                query = parsed.get("query", "")
                category = parsed.get("category")
                
                if self.verbose:
                    print(f"🔍 Action: {action_type}('{query}', category={category})")
                
                # DB 검색 실행
                if action_type == "search":
                    # Hybrid Searcher 또는 기본 Searcher
                    if isinstance(self.searcher, HybridSearcher):
                        search_results = self.searcher.search(query, category=category, limit=5)
                    else:
                        search_results = self.searcher.search(query, category=category, limit=5)
                elif action_type == "related":
                    # related는 MapleDBSearcher만 지원
                    if isinstance(self.searcher, HybridSearcher):
                        # Hybrid에서는 일반 검색으로 대체
                        search_results = self.searcher.search(query, category=category, limit=5)
                    else:
                        search_results = self.searcher.get_related_entities(query)
                else:
                    search_results = []
                
                # 결과 포맷팅
                observation = self._format_search_results(search_results, action_type)
                
                actions.append({
                    "action_type": action_type,
                    "query": query,
                    "category": category,
                    "results": search_results
                })
                
                if self.verbose:
                    print(f"👀 Observation:\n{observation}\n")
                
                # Observation을 대화 히스토리에 추가
                self.conversation_history.append(AIMessage(content=response_text))
                self.conversation_history.append(HumanMessage(
                    content=f"[OBSERVATION]\n{observation}\n\n계속 생각해주세요. 정보가 충분하면 FINAL_ANSWER를 작성하고, 부족하면 THOUGHT와 ACTION을 반복하세요."
                ))
            
            else:
                # 파싱 실패 - 재시도
                logger.warning(f"응답 파싱 실패: {response_text[:100]}")
                self.conversation_history.append(AIMessage(content=response_text))
                self.conversation_history.append(HumanMessage(
                    content="응답 형식이 잘못되었습니다. [THOUGHT], [ACTION], [FINAL_ANSWER] 중 하나를 사용해주세요."
                ))
        
        # 최대 반복 초과
        logger.warning(f"최대 반복 횟수({self.max_iterations}) 초과")
        return {
            "answer": "죄송합니다. 충분한 정보를 찾지 못했습니다.",
            "thoughts": thoughts,
            "actions": actions,
            "iterations": self.max_iterations,
            "success": False
        }
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트"""
        return """당신은 메이플스토리 게임 지식 검색 Agent입니다.

사용자의 질문에 답변하기 위해 **Thought-Action-Observation** 루프를 반복하세요.

## 응답 형식

### 1. THOUGHT (생각)
정보가 부족한지, 무엇을 검색해야 하는지 생각합니다.
```
[THOUGHT]
<생각 내용>
```

### 2. ACTION (행동)
DB 검색을 실행합니다. 반드시 JSON 형식으로 작성하세요.

**기본 검색:**
```
[ACTION]
{
  "action_type": "search",
  "query": "검색어",
  "category": "MAP|NPC|ITEM|MONSTER|null"
}
```

**중요: category는 반드시 MAP, NPC, ITEM, MONSTER 중 하나이거나 null이어야 합니다!**
- "직업", "퀘스트" 같은 값은 사용 불가 → null 사용
- NPC 관련 검색은 category를 "NPC" 또는 null로 설정

**연관 검색:**
```
[ACTION]
{
  "action_type": "related",
  "query": "엔티티_이름"
}
```

### 3. OBSERVATION
시스템이 자동으로 검색 결과를 제공합니다.

### 4. FINAL_ANSWER (최종 답변)
충분한 정보를 수집했으면 최종 답변을 작성합니다.
```
[FINAL_ANSWER]
<최종 답변 내용>
```

## 예시

사용자: "아이스진 사려면 어디로 가야 하나요?"

```
[THOUGHT]
"아이스진"이 무엇인지, 어디서 살 수 있는지 검색해야겠다.

[ACTION]
{"action_type": "search", "query": "아이스진", "category": null}
```

→ [OBSERVATION] 아이스진 = 아이템, 리스항구의 페이슨이 판매

```
[THOUGHT]
정보가 충분하다. 최종 답변을 작성하자.

[FINAL_ANSWER]
아이스진은 **리스항구**에 있는 **페이슨 NPC**에게서 구매할 수 있습니다.
가격은 4800 메소이며, 청바지 종류의 하의 장비입니다.
```

## 규칙
1. 한 번에 하나씩만 작성 (THOUGHT → ACTION 또는 FINAL_ANSWER)
2. 정보가 부족하면 추가 검색 (최대 5회)
3. ACTION의 JSON은 반드시 올바른 형식으로
4. FINAL_ANSWER는 친절하고 자세하게

이제 시작하세요!"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """LLM 응답 파싱 (THOUGHT와 ACTION이 함께 있으면 ACTION 우선)"""
        response = response.strip()
        
        # FINAL_ANSWER
        if "[FINAL_ANSWER]" in response:
            content = response.split("[FINAL_ANSWER]", 1)[1].strip()
            return {"type": "FINAL_ANSWER", "content": content}
        
        # ACTION (THOUGHT보다 우선)
        if "[ACTION]" in response:
            action_part = response.split("[ACTION]", 1)[1].strip()
            
            # JSON 추출
            json_str = None
            try:
                # JSON 블록 찾기
                # 1. ```json...``` 형식
                if "```json" in action_part:
                    json_str = action_part.split("```json", 1)[1].split("```", 1)[0].strip()
                # 2. ```...``` 형식 (일반 코드 블록)
                elif "```" in action_part:
                    # ``` 다음부터 다음 ```까지
                    parts = action_part.split("```")
                    if len(parts) >= 2:
                        # 첫 번째 ``` 안의 내용
                        json_str = parts[1].strip()
                # 3. {...} 직접 찾기
                elif "{" in action_part and "}" in action_part:
                    start = action_part.index("{")
                    end = action_part.rindex("}") + 1
                    json_str = action_part[start:end]
                else:
                    # JSON이 바로 시작하는 경우
                    json_str = action_part.strip()
                
                # 빈 문자열 체크
                if not json_str or json_str.isspace():
                    # 강제로 {} 찾기
                    if "{" in action_part and "}" in action_part:
                        start = action_part.index("{")
                        end = action_part.rindex("}") + 1
                        json_str = action_part[start:end]
                
                logger.info(f"🔍 JSON 파싱 시도: {json_str[:100] if json_str else 'EMPTY'}")
                
                # JSON 파싱 (null → None 자동 변환)
                action_data = json.loads(json_str)
                
                # THOUGHT도 함께 추출
                thought = ""
                if "[THOUGHT]" in response:
                    thought = response.split("[THOUGHT]", 1)[1].split("[ACTION]", 1)[0].strip()
                
                # 카테고리 검증 (유효한 값만 허용)
                valid_categories = ["MAP", "NPC", "ITEM", "MONSTER"]
                category = action_data.get("category")
                if category and category.upper() not in valid_categories:
                    logger.warning(f"⚠️ 유효하지 않은 카테고리: '{category}' → None으로 변환")
                    category = None
                elif category:
                    category = category.upper()  # 대소문자 정규화
                
                logger.info(f"✅ JSON 파싱 성공: {action_data} (category={category})")
                
                return {
                    "type": "ACTION",
                    "action_type": action_data.get("action_type", "search"),
                    "query": action_data.get("query", ""),
                    "category": category,  # 검증된 카테고리만 사용
                    "thought": thought
                }
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error(f"❌ JSON 파싱 실패: {e}")
                logger.error(f"   JSON 문자열: {json_str}")
                logger.error(f"   Action part: {action_part[:200]}")
                # 파싱 실패해도 THOUGHT는 추출 시도
                if "[THOUGHT]" in response:
                    thought = response.split("[THOUGHT]", 1)[1].split("[ACTION]", 1)[0].strip()
                    return {"type": "THOUGHT", "content": thought}
                return {"type": "UNKNOWN", "content": response}
        
        # THOUGHT (ACTION이 없을 때만)
        if "[THOUGHT]" in response:
            content = response.split("[THOUGHT]", 1)[1].strip()
            return {"type": "THOUGHT", "content": content}
        
        return {"type": "UNKNOWN", "content": response}
    
    def _format_search_results(
        self, 
        results: Any,
        action_type: str
    ) -> str:
        """검색 결과를 텍스트로 포맷팅"""
        if action_type == "related":
            # 연관 검색 결과
            if not results or not isinstance(results, dict):
                return "검색 결과가 없습니다."
            
            output = []
            source = results.get("source", {})
            output.append(f"[기준: {source.get('canonical_name', '?')}]")
            output.append(f"카테고리: {source.get('category', '?')}")
            output.append(f"설명: {source.get('description', '없음')}\n")
            
            for key, items in results.items():
                if key == "source" or not items:
                    continue
                
                label = {
                    "related_npcs": "연관 NPC",
                    "related_items": "연관 아이템",
                    "related_maps": "연관 맵",
                    "related_monsters": "연관 몬스터"
                }.get(key, key)
                
                output.append(f"\n{label} ({len(items)}개):")
                for item in items[:3]:  # 최대 3개만
                    data = item.get("data", {})
                    output.append(f"  - {data.get('canonical_name', '?')}: {data.get('description', '')[:50]}...")
            
            return "\n".join(output)
        
        else:
            # 일반 검색 결과
            if not results:
                return "검색 결과가 없습니다."
            
            output = [f"검색 결과 {len(results)}개:\n"]
            for idx, result in enumerate(results[:5], 1):  # 최대 5개
                data = result["data"]
                output.append(f"{idx}. {data['canonical_name']} ({data['category']})")
                output.append(f"   설명: {data.get('description', '없음')}")
                
                # detail_data 중요 정보 추출
                detail = data.get("detail_data", {})
                if detail:
                    if data['category'] == 'ITEM':
                        output.append(f"   종류: {detail.get('item_type', '?')}")
                        output.append(f"   획득: {', '.join(detail.get('obtainable_from', []))}")
                    elif data['category'] == 'MONSTER':
                        output.append(f"   레벨: {detail.get('level', '?')}")
                        output.append(f"   HP: {detail.get('hp', '?')}")
                        drops = detail.get('drops', [])
                        if drops:
                            drop_names = [d.get('item_name', '?') for d in drops[:3]]
                            output.append(f"   드랍: {', '.join(drop_names)}")
                    elif data['category'] == 'MAP':
                        output.append(f"   위치: {detail.get('region', '?')}")
                        npcs = detail.get('resident_npcs', [])
                        if npcs:
                            output.append(f"   NPC: {', '.join(npcs[:3])}")
                    elif data['category'] == 'NPC':
                        output.append(f"   위치: {detail.get('location', '?')}")
                        services = detail.get('services', [])
                        if services:
                            output.append(f"   서비스: {', '.join(services)}")
                
                output.append("")
            
            return "\n".join(output)


# 편의 함수
def ask_maple_agent(
    db: Session,
    llm: ChatOllama,
    question: str,
    max_iterations: int = 5,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    간단한 Agent 실행 함수
    
    Usage:
        result = ask_maple_agent(db, llm, "아이스진 사려면 어디로 가야 하나요?")
        print(result["answer"])
    """
    agent = SearchAgent(db, llm, max_iterations, verbose)
    return agent.run(question)
