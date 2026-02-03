#!/usr/bin/env python3
"""
Search Agent 테스트 스크립트
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

# Import
from database.session import SessionLocal
from langchain_community.chat_models import ChatOllama
from config.settings import settings
from src.agents.search_agent import SearchAgent
import json


def test_agent(question: str, max_iterations: int = 5):
    """Agent 테스트"""
    
    db = SessionLocal()
    print(db)

    try:
        # LLM 초기화
        # Ollama 로컬 모델 사용 (한국어 지원 우선순위: gemma3 > llama3.1)
        model_name = "hf.co/bartowski/google_gemma-3-12b-it-GGUF:Q4_K_M"  # 또는 "llama3.1:latest"
        base_url = "http://localhost:11434"
        
        print(f"🤖 LLM 초기화: {model_name}")
        print(f"📡 Base URL: {base_url}")
        
        from langchain_community.llms import Ollama
        from langchain_community.chat_models import ChatOllama as CommunityChatOllama
        
        llm = CommunityChatOllama(
            base_url=base_url,
            model=model_name,
            temperature=0.1
        )
        
        # Agent 실행
        print("\n" + "="*80)
        print(f"❓ 질문: {question}")
        print("="*80 + "\n")
        
        # Hybrid Search 사용 (Milvus 실패해도 PostgreSQL로 동작)
        agent = SearchAgent(
            db, 
            llm, 
            max_iterations=max_iterations, 
            verbose=True,
            use_hybrid=True  # Hybrid Search 활성화
        )
        result = agent.run(question)
        
        # 결과 출력
        print("\n" + "="*80)
        print("📊 Agent 실행 결과")
        print("="*80)
        print(f"\n✅ 성공: {result['success']}")
        print(f"🔄 반복 횟수: {result['iterations']}/{max_iterations}")
        print(f"💭 생각 횟수: {len(result['thoughts'])}")
        print(f"🔍 검색 횟수: {len(result['actions'])}")
        
        print(f"\n📝 최종 답변:")
        print("-" * 80)
        print(result['answer'])
        print("-" * 80)
        
        # 상세 정보
        if result['thoughts']:
            print(f"\n💭 Thoughts:")
            for idx, thought in enumerate(result['thoughts'], 1):
                print(f"  {idx}. {thought[:100]}...")
        
        if result['actions']:
            print(f"\n🔍 Actions:")
            for idx, action in enumerate(result['actions'], 1):
                print(f"  {idx}. {action['action_type']}('{action['query']}', category={action.get('category')})")
                print(f"     → {len(action['results']) if isinstance(action['results'], list) else 1}개 결과")
        
        print("\n" + "="*80)
        
        # JSON 저장
        output_file = PROJECT_ROOT / "logs" / "agent_result.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 결과 저장: {output_file}")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📚 사용법:")
        print("  python test_search_agent.py <질문> [최대반복횟수]")
        print("\n예시:")
        print('  python test_search_agent.py "아이스진 사려면 어디로 가야 하나요?"')
        print('  python test_search_agent.py "주황버섯은 어디서 잡나요?" ')
        print('  python test_search_agent.py "헤네시스에서 할 수 있는 일은?"')
        sys.exit(1)
    
    question = sys.argv[1]
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    test_agent(question, max_iterations)
