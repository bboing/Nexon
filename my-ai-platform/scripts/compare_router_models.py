#!/usr/bin/env python3
"""
Router 모델 비교 테스트 (llama3.1 vs gemma3-12b)
"""
import sys
from pathlib import Path
import time

# 경로 설정
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LANGCHAIN_APP_DIR = PROJECT_ROOT / "langchain_app"
sys.path.insert(0, str(LANGCHAIN_APP_DIR))

# .env 로드
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from langchain_community.chat_models import ChatOllama
from src.agents.router_agent import RouterAgent, QueryType


# 테스트 질문들
TEST_CASES = [
    ("아이스진 가격은?", QueryType.SIMPLE_LOOKUP, "가격_조회"),
    ("페이슨은 누구야?", QueryType.SIMPLE_LOOKUP, "엔티티_정보"),
    ("아이스진 어디서 나와?", QueryType.RELATIONSHIP, "드롭_정보_확인"),
    ("헤네시스에서 커닝시티 가는 법?", QueryType.RELATIONSHIP, "길찾기"),
    ("초보자 추천 장비", QueryType.SEMANTIC, "추천_요청"),
    ("도적에게 좋은 사냥터", QueryType.SEMANTIC, "추천_요청"),
    ("아이스진 사고 다음에 뭐 사야 해?", QueryType.COMPLEX, "추천_요청"),
]


def test_model(model_name: str, test_cases: list):
    """특정 모델로 테스트"""
    print(f"\n{'='*80}")
    print(f"🤖 모델: {model_name}")
    print(f"{'='*80}")
    
    # LLM 초기화
    llm = ChatOllama(
        base_url="http://localhost:11434",
        model=model_name,
        temperature=0.1
    )
    
    router = RouterAgent(llm, verbose=False)
    
    results = []
    total_time = 0
    
    for idx, (question, expected_type, expected_intent_keyword) in enumerate(test_cases, 1):
        print(f"\n[{idx}/{len(test_cases)}] {question}")
        
        # 시간 측정
        start = time.time()
        result = router.classify(question)
        elapsed = time.time() - start
        total_time += elapsed
        
        # 결과 평가
        type_correct = result['type'] == expected_type
        intent_match = expected_intent_keyword in result.get('intent', '').lower()
        
        # 출력
        print(f"   타입: {result['type']} {'✅' if type_correct else '❌'}")
        print(f"   의도: {result.get('intent', 'N/A')} {'✅' if intent_match else '⚠️'}")
        print(f"   신뢰도: {result['confidence']:.2f}")
        print(f"   시간: {elapsed:.2f}초")
        
        results.append({
            "question": question,
            "expected_type": expected_type,
            "actual_type": result['type'],
            "type_correct": type_correct,
            "intent": result.get('intent', 'N/A'),
            "intent_match": intent_match,
            "confidence": result['confidence'],
            "time": elapsed
        })
    
    # 통계
    type_accuracy = sum(1 for r in results if r['type_correct']) / len(results) * 100
    intent_accuracy = sum(1 for r in results if r['intent_match']) / len(results) * 100
    avg_time = total_time / len(results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    print(f"\n{'='*80}")
    print(f"📊 {model_name} 통계")
    print(f"{'='*80}")
    print(f"타입 정확도: {type_accuracy:.1f}%")
    print(f"의도 매칭: {intent_accuracy:.1f}%")
    print(f"평균 신뢰도: {avg_confidence:.2f}")
    print(f"평균 시간: {avg_time:.2f}초")
    print(f"총 시간: {total_time:.2f}초")
    
    return {
        "model": model_name,
        "type_accuracy": type_accuracy,
        "intent_accuracy": intent_accuracy,
        "avg_confidence": avg_confidence,
        "avg_time": avg_time,
        "total_time": total_time,
        "results": results
    }


def compare_models():
    """두 모델 비교"""
    print("\n" + "🔬"*40)
    print("Router 모델 비교 테스트")
    print("🔬"*40)
    
    # 모델 1: llama3.1
    llama_stats = test_model("llama3.1:latest", TEST_CASES)
    
    # 모델 2: gemma3-12b
    gemma_stats = test_model(
        "hf.co/bartowski/google_gemma-3-12b-it-GGUF:Q4_K_M", 
        TEST_CASES
    )
    
    # 비교 결과
    print(f"\n{'='*80}")
    print("🏆 최종 비교")
    print(f"{'='*80}")
    
    print(f"\n{'항목':<20} {'llama3.1':<15} {'gemma3-12b':<15} {'승자':<10}")
    print("-" * 80)
    
    # 타입 정확도
    print(f"{'타입 정확도':<20} "
          f"{llama_stats['type_accuracy']:.1f}%{'':<10} "
          f"{gemma_stats['type_accuracy']:.1f}%{'':<10} "
          f"{'🏆 Gemma' if gemma_stats['type_accuracy'] > llama_stats['type_accuracy'] else '🏆 Llama' if llama_stats['type_accuracy'] > gemma_stats['type_accuracy'] else '🤝 동점'}")
    
    # 의도 매칭
    print(f"{'의도 매칭':<20} "
          f"{llama_stats['intent_accuracy']:.1f}%{'':<10} "
          f"{gemma_stats['intent_accuracy']:.1f}%{'':<10} "
          f"{'🏆 Gemma' if gemma_stats['intent_accuracy'] > llama_stats['intent_accuracy'] else '🏆 Llama' if llama_stats['intent_accuracy'] > gemma_stats['intent_accuracy'] else '🤝 동점'}")
    
    # 평균 신뢰도
    print(f"{'평균 신뢰도':<20} "
          f"{llama_stats['avg_confidence']:.2f}{'':<12} "
          f"{gemma_stats['avg_confidence']:.2f}{'':<12} "
          f"{'🏆 Gemma' if gemma_stats['avg_confidence'] > llama_stats['avg_confidence'] else '🏆 Llama' if llama_stats['avg_confidence'] > gemma_stats['avg_confidence'] else '🤝 동점'}")
    
    # 평균 시간 (낮을수록 좋음)
    print(f"{'평균 시간':<20} "
          f"{llama_stats['avg_time']:.2f}초{'':<10} "
          f"{gemma_stats['avg_time']:.2f}초{'':<10} "
          f"{'🏆 Llama' if llama_stats['avg_time'] < gemma_stats['avg_time'] else '🏆 Gemma' if gemma_stats['avg_time'] < llama_stats['avg_time'] else '🤝 동점'}")
    
    print("\n" + "="*80)
    
    # 추천
    llama_score = (
        llama_stats['type_accuracy'] * 0.4 +
        llama_stats['intent_accuracy'] * 0.3 +
        llama_stats['avg_confidence'] * 100 * 0.2 -
        llama_stats['avg_time'] * 10 * 0.1
    )
    
    gemma_score = (
        gemma_stats['type_accuracy'] * 0.4 +
        gemma_stats['intent_accuracy'] * 0.3 +
        gemma_stats['avg_confidence'] * 100 * 0.2 -
        gemma_stats['avg_time'] * 10 * 0.1
    )
    
    print(f"\n💡 추천:")
    if gemma_score > llama_score + 5:
        print(f"   🏆 gemma3-12b 추천!")
        print(f"   - 더 정확함 (타입: {gemma_stats['type_accuracy']:.1f}%, 의도: {gemma_stats['intent_accuracy']:.1f}%)")
        print(f"   - 약간 느리지만 ({gemma_stats['avg_time']:.2f}초 vs {llama_stats['avg_time']:.2f}초)")
        print(f"   - 정확도가 속도보다 중요!")
    elif llama_score > gemma_score + 5:
        print(f"   🏆 llama3.1 추천!")
        print(f"   - 충분히 정확함 (타입: {llama_stats['type_accuracy']:.1f}%)")
        print(f"   - 훨씬 빠름 ({llama_stats['avg_time']:.2f}초)")
        print(f"   - Router는 속도가 중요!")
    else:
        print(f"   🤝 비슷한 성능!")
        print(f"   - 속도 우선이면 llama3.1")
        print(f"   - 정확도 우선이면 gemma3-12b")


if __name__ == "__main__":
    compare_models()
