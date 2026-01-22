import subprocess
import sys
from pathlib import Path
from mlx_lm import load, generate

# 1. 학습된 모델 경로 (fuse 하기 전 어댑터나, fuse된 모델 경로)
# 주의: 아까 학습한 결과물이 있는 폴더로 지정!
base_path = Path(__file__).resolve().parent.parent
model_path = base_path / "models" / "llama-game-npc-mlx-dequantized"
gguf_output = base_path / "models" / "gguf" / "llama-game-npc.gguf"
# 만약 fuse된 걸 테스트하려면: "./models/llama-game-npc-merged-fp16"

print(f"⏳ 모델 로드 중: {model_path}")
model, tokenizer = load(model_path)

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
prompt = header + modelfile_content

# 3. 생성
print("💬 생성 시작...")
response = generate(
    model, 
    tokenizer, 
    prompt=prompt, 
    verbose=True, 
    max_tokens=100,
)

print("\n=== 결과 ===")
print(response)