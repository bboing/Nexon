#!/usr/bin/env python3
"""
MLX 학습 모델 테스트 스크립트
학습된 LoRA 어댑터를 로드하여 대화 테스트
"""

from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import sys

def test_model(prompt: str = None):
    """학습된 모델로 테스트"""
    
    print("🍎 MLX 학습 모델 로딩 중...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 모델 + 어댑터 로드
    model_name = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    adapter_path = "../models/llama-game-npc-mlx"
    
    print(f"📦 기본 모델: {model_name}")
    print(f"🎨 LoRA 어댑터: {adapter_path}\n")
    
    model, tokenizer = load(
        model_name,
        adapter_path=adapter_path
    )
    
    print("✅ 로딩 완료!\n")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 테스트 프롬프트
    test_prompts = [
        "플레이어: 안녕하세요?\nNPC:",
        "플레이어: 마법사로 전직할래요\nNPC:",
        "플레이어: 전사로 전직하고 싶어요\nNPC:",
        "플레이어: 도적으로 전직할래요\nNPC:",
        "플레이어: 궁수로 전직하려면 어떻게 해야 하나요\nNPC:",
    ]
    
    # 커스텀 프롬프트가 있으면 사용
    if prompt:
        test_prompts = [prompt]
    
    # 각 프롬프트 테스트
    for i, prompt in enumerate(test_prompts, 1):
        print(f"🎮 테스트 {i}/{len(test_prompts)}")
        print(f"📝 프롬프트:\n{prompt}")
        print(f"\n🤖 AI 응답:")
        
        sampler = make_sampler(temp=0.7, top_p=0.9)
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=100,
            verbose=False,
            sampler=sampler,
        )
        
        print(response)
        print("\n" + "━"*50 + "\n")
    
    print("✅ 테스트 완료!")
    print("\n💡 팁:")
    print("   - 커스텀 테스트: python test_mlx_model.py \"플레이어: 안녕하세요?\\nNPC:\"")
    print("   - 대화형 모드: python interactive_chat.py")

def interactive_mode():
    """대화형 모드"""
    print("🍎 MLX 학습 모델 - 대화형 모드")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 모델 로드
    model_name = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    adapter_path = "../models/llama-game-npc-mlx"
    
    print(f"📦 로딩 중... ", end="", flush=True)
    model, tokenizer = load(model_name, adapter_path=adapter_path)
    print("완료! ✅\n")
    
    print("💬 대화를 시작합니다. (종료: 'exit' 또는 Ctrl+C)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    while True:
        try:
            # 사용자 입력
            user_input = input("👤 플레이어: ")
            
            if user_input.lower() in ['exit', 'quit', '종료']:
                print("\n👋 대화를 종료합니다.")
                break
            
            # 프롬프트 구성
            prompt = f"플레이어: {user_input}\nNPC:"
            
            # 응답 생성
            print("🤖 NPC: ", end="", flush=True)
            sampler = make_sampler(temp=0.7, top_p=0.9)
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=100,
                verbose=False,
                sampler=sampler,
            )
            
            # NPC 응답만 출력 (프롬프트 제외)
            npc_response = response.split("NPC:")[-1].strip()
            print(npc_response)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 대화를 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류: {e}")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            # 대화형 모드
            interactive_mode()
        else:
            # 커스텀 프롬프트
            custom_prompt = " ".join(sys.argv[1:])
            test_model(custom_prompt)
    else:
        # 기본 테스트
        test_model()
