#!/usr/bin/env python3
"""
LLM 연결 테스트
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LANGCHAIN_APP_DIR = PROJECT_ROOT / "langchain_app"
sys.path.insert(0, str(LANGCHAIN_APP_DIR))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

print("✅ 1. 환경 설정 완료")

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

print("✅ 2. LangChain import 완료")

# LLM 초기화
model_name = "llama3.1:latest"  # 빠른 테스트용
base_url = "http://localhost:11434"

print(f"\n🤖 LLM 초기화 중...")
print(f"   모델: {model_name}")
print(f"   Base URL: {base_url}")

try:
    llm = ChatOllama(
        base_url=base_url,
        model=model_name,
        temperature=0.1,
        timeout=30  # 30초 타임아웃
    )
    print("✅ 3. LLM 객체 생성 완료")
    
    # 간단한 테스트
    print("\n" + "="*80)
    print("💬 LLM 테스트: '안녕하세요'")
    print("="*80)
    print("\n기다리는 중... (최대 30초)")
    
    response = llm.invoke([HumanMessage(content="안녕하세요. 간단히 인사해주세요.")])
    
    print(f"\n🤖 LLM 응답:")
    print("-" * 80)
    print(response.content)
    print("-" * 80)
    
    print("\n✅ 4. LLM 테스트 완료!")
    print("\n이제 Agent를 실행해볼 수 있어요!")
    
except Exception as e:
    print(f"\n❌ LLM 테스트 실패: {e}")
    print("\n가능한 원인:")
    print("1. Ollama가 실행 중이 아님 → ollama serve 실행")
    print("2. 모델이 없음 → ollama pull llama3.1")
    print("3. 포트가 다름 → .env 파일 확인")
    import traceback
    traceback.print_exc()
