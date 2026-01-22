#!/usr/bin/env python3
"""
Apple MLX를 이용한 LoRA 파인튜닝
M1/M2/M3 Mac 최적화
"""

from mlx_lm import load, generate
from mlx_lm.tuner import train
from mlx_lm.utils import load as mlx_load, save_config
import mlx.core as mx
import json
import random
from pathlib import Path

print("🍎 Apple MLX 파인튜닝 시작!")
print(f"   MLX Device: Metal GPU")
print(f"   Memory: Unified Memory")

# ============================================================
# 1. 설정
# ============================================================
CONFIG = {
    # 모델 설정
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "adapter_file": "adapters.safetensors",  # LoRA 어댑터 저장 파일
    
    # 학습 설정
    "train": True,
    "batch_size": 8,
    "iters": 600,  # 학습 iteration (테스트: 100, 실전: 1000+)
    "val_batches": 25,
    "learning_rate": 1e-5,
    "steps_per_report": 10,
    "steps_per_eval": 100,
    "save_every": 50,
    "test": False,
    "test_batches": 100,
    
    # LoRA 설정
    "lora_layers": 32,  # LoRA를 적용할 레이어 수
    "lora_rank": 16,  # LoRA rank (8~32 권장)
    "lora_scale": 20.0,
    
    # 데이터셋
    "data": "../data",  # 데이터 디렉토리
    "seed": 42,
}

# ============================================================
# 2. 데이터셋 준비 (Alpaca 형식)
# ============================================================

data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
input_file = data_dir / "input_data" / "maple_npc.json" # 원본 데이터 
train_path = data_dir / "train.jsonl"   # 변환된 학습용 데이터

# 데이터 로드
with open(input_file, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"🔄 변환 시작: 총 {len(raw_data)}개 데이터")

converted_data = []

# 2. 루프 돌면서 포맷 변환 (핵심 로직)
for item in raw_data:
    system_content = f"당신은 '{item['City']}'에 거주하는 NPC '{item['NPC_Name']}'입니다. {item['instruction']}"
    
    entry = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": item['input']},
            {"role": "assistant", "content": item['output']}
        ]
    }
    converted_data.append(entry)

# 3. JSONL 파일로 저장 (한 줄에 json 하나씩)
with open(train_path, "w", encoding="utf-8") as f:
    # row_count = sum(1 for _ in f)
    for entry in converted_data:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n") # 줄바꿈 필수



# valid.jsonl 생성 (validation)
if len(converted_data) > 1:
    first_msg = converted_data[0]['messages'][0]['content']
    last_msg = converted_data[-1]['messages'][0]['content']
    
    if first_msg == last_msg:
        print("🚨 [경고] 여전히 모든 데이터가 똑같습니다! 원본(raw_data)이 중복인지 확인하세요.")
    else:
        print("✨ [성공] 데이터가 서로 다릅니다. 이제 랜덤 추출이 정상 작동합니다.")

    valid_path = data_dir / "valid.jsonl"
    random_valid_data = random.sample(converted_data, min(10, len(converted_data)))
    print(f"random_valid_data : {random_valid_data}")

    with open(valid_path, "w", encoding="utf-8") as f:
        for item in random_valid_data:  # 랜덤
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

        
print(f"✅ 데이터셋 준비 완료!")
print(f"   Train: {train_path} ({len(converted_data)}개)")
print(f"   Valid: {valid_path} (10개)")

# ============================================================
# 3. 모델 로드
# ============================================================
print(f"\n📦 모델 다운로드 중: {CONFIG['model']}")
print("   (첫 실행 시 시간이 걸립니다...)")

try:
    model, tokenizer = load(CONFIG['model'])
    print("✅ 모델 로드 완료!")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    print("\n💡 해결 방법:")
    print("   1. 인터넷 연결 확인")
    print("   2. Hugging Face 토큰 설정:")
    print("      huggingface-cli login")
    exit(1)

# ============================================================
# 4. 파인튜닝 실행
# ============================================================
print("\n🚀 MLX LoRA 파인튜닝 시작!")
print(f"   Iterations: {CONFIG['iters']}")
print(f"   LoRA Rank: {CONFIG['lora_rank']}")
print(f"   Learning Rate: {CONFIG['learning_rate']}")
print("")

# 출력 디렉토리
output_dir = Path(__file__).parent.parent / "models" / "llama-game-npc-mlx"
output_dir.mkdir(parents=True, exist_ok=True)

# mlx-lm train 명령어 구성
import subprocess
import sys

cmd = [
    sys.executable, "-m", "mlx_lm.lora",
    "--model", CONFIG['model'],
    "--train",
    "--data", str(data_dir),
    "--batch-size", str(CONFIG['batch_size']),
    "--iters", str(CONFIG['iters']),
    "--learning-rate", str(CONFIG['learning_rate']),
    "--num-layers", str(CONFIG['lora_layers']),
    "--adapter-path", str(output_dir),
]

print("📝 실행 명령어:")
print(" ".join(cmd))
print("")

# 학습 실행
try:
    result = subprocess.run(cmd, check=True, cwd=output_dir)
    print("\n✅ 파인튜닝 완료!")
except subprocess.CalledProcessError as e:
    print(f"\n❌ 파인튜닝 실패: {e}")
    exit(1)

# ============================================================
# 5. 저장
# ============================================================
print(f"\n💾 모델 저장 위치:")
print(f"   {output_dir}")
print(f"   ├─ adapters.safetensors (LoRA 가중치)")
print(f"   └─ config.json (설정)")

# ============================================================
# 6. 추론 테스트
# ============================================================
print("\n🎮 추론 테스트:")

# LoRA 어댑터와 함께 모델 로드
try:
    model, tokenizer = load(
        CONFIG['model'],
        adapter_path=str(output_dir)
    )
    
    test_prompt = "도적으로 전직하고 싶어요 NPC:"
    
    print(f"\n입력: {test_prompt}")
    print("출력: ", end="")
    
    response = generate(
        model,
        tokenizer,
        prompt=test_prompt,
        max_tokens=100,
        temp=0.7,
    )
    
    print(response)
    
except Exception as e:
    print(f"❌ 추론 실패: {e}")

print("\n" + "="*60)
print("✅ MLX 파인튜닝 완료! 🎉")
print("="*60)

print("\n📋 다음 단계:")
print("1. Ollama Modelfile 생성:")
print("   - adapters.safetensors를 Ollama 형식으로 변환")
print("")
print("2. 추가 학습:")
print("   - data/train.jsonl에 더 많은 데이터 추가")
print("   - iters 값 증가 (1000+)")
print("")
print("3. 평가:")
print("   - 다양한 NPC 시나리오로 테스트")
print("")

