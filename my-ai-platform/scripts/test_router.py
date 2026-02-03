#!/usr/bin/env python3
"""Router Agent 테스트"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LANGCHAIN_APP_DIR = PROJECT_ROOT / "langchain_app"
sys.path.insert(0, str(LANGCHAIN_APP_DIR))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from src.agents.router_agent import RouterAgent

# 테스트 쿼리
TEST_QUERIES = [
    "도적 사냥터 추천",
    "도적 전직 어디서?",
    "다크로드 어디 있어?",
    "아이스진 어디서 사?",
    "스포아 어디서 잡아?",
    "헤네시스 가는 법",
    "20레벨 사냥터",
    "궁수로 전직하려면?",
]

def main():
    print("\n" + "="*80)
    print("🧭 Router Agent 테스트")
    print("="*80 + "\n")
    
    router = RouterAgent(verbose=False)
    
    for query in TEST_QUERIES:
        print(f"\n❓ Query: '{query}'")
        print("-" * 80)
        
        result = router.route(query)
        
        print(f"   🎯 Intent: {result['intent']}")
        print(f"   📁 Categories: {result['categories']}")
        print(f"   🔍 Strategy: {result['strategy']}")
        print(f"   🔑 Keywords: {result['keywords']}")
        print(f"   💭 Reasoning: {result['reasoning']}")
    
    print("\n" + "="*80)
    print("✅ 테스트 완료!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
