#!/usr/bin/env python3
"""
MLX 모델을 GGUF로 변환하여 Ollama에서 사용 가능하게 만들기
"""

import subprocess
import os
from pathlib import Path

def convert_to_gguf():
    """MLX 어댑터를 병합하고 GGUF로 변환"""
    
    print("🔄 MLX → GGUF 변환 시작")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    print("   (llama.cpp의 convert.py 필요)\n")
    
    

def convert_to_gguf():
    #경로 정의
    base_path = Path(__file__).resolve().parent.parent
    
    # ⭐ 이미 병합된 모델 경로
    merged_model_path = base_path / "models" / "llama-game-npc-mlx-dequantized"
    gguf_output = base_path / "models" / "gguf" / "llama-game-npc.gguf"
    gguf_output.parent.mkdir(parents=True, exist_ok=True)
    # 병합된 모델이 있는지 확인
    if not merged_model_path.exists():
        print(f"❌ 병합된 모델이 없습니다: {merged_model_path}")
        print("💡 먼저 dequantize_mlx.py를 실행하세요!")
        return
    
    print("1️⃣  병합된 모델 확인 ✅")
    print(f"   경로: {merged_model_path}\n")
    
    # ⭐ 바로 GGUF 변환 시작
    print("2️⃣  GGUF 변환 중...")
    

    # llama.cpp 확인
    print(f"Path.home(): {Path.home()}")
    llama_cpp_path = Path.home() / "bboing/ollama_model/my-ai-platform/training/llama.cpp"
    if not llama_cpp_path.exists():
        print("❌ llama.cpp가 설치되지 않았습니다.")
        return
    
    # GGUF 변환
    print("🔄 MLX → GGUF 변환 시작")
    convert_cmd = [
        "python",
        str(llama_cpp_path / "convert_hf_to_gguf.py"),
        str(merged_model_path),
        "--outfile", str(gguf_output),
        "--outtype", "f16",  # fp16 precision
    ]
    
    try:
        subprocess.run(convert_cmd, check=True)
        print("✅ GGUF 변환 완료!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ GGUF 변환 실패: {e}")
        return
    
    print("3️⃣  Ollama Modelfile 생성 중...\n")
    
    # Ollama Modelfile 생성
    modelfile_path = Path("../models/Modelfile")
    header = f"FROM {gguf_output.absolute()}\n"
    modelfile_content = """
SYSTEM \"\"\"당신은 이 게임 세계의 살아있는 NPC입니다.
다음 원칙을 반드시 지켜 대답하세요:
1. 언어: 무조건 자연스러운 '한국어'만 사용하세요. (영어, 한자 금지)
2. 태도: AI 비서처럼 딱딱하게 굴지 말고, 맡은 역할(Role)에 몰입하여 연기하세요.
3. 지식: 당신이 알고 있는 설정 내에서만 대답하고, 모르는 내용은 "그건 내 알 바 아니네" 혹은 "모르겠는데?"와 같이 NPC스럽게 거절하세요. 없는 사실을 지어내지 마세요.
4. 형식: 답변은 너무 길지 않게, 대화하듯이 2~3문장으로 간결하게 하세요.\"\"\"

TEMPLATE \"\"\"{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .User }}<|start_header_id|>user<|end_header_id|>

{{ .User }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>\"\"\"

PARAMETER temperature 0.6

PARAMETER num_ctx 4096

PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
"""
    modelfile_content = header + modelfile_content
    modelfile_path.write_text(modelfile_content)
    print(f"✅ Modelfile 생성: {modelfile_path}\n")
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 변환 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    print("🚀 Ollama에 등록하기:")
    print(f"   cd {Path('../models').absolute()}")
    print(f"   ollama create game-npc -f Modelfile")
    print()
    print("💬 테스트하기:")
    print("   ollama run game-npc")
    print()
    print("🌐 WebUI에서 사용:")
    print("   http://localhost:8090 접속")
    print("   모델 선택: game-npc")



if __name__ == "__main__":
    print("\n⚠️  주의: 이 스크립트는 llama.cpp가 설치되어 있어야 합니다.\n")
    convert_to_gguf()
