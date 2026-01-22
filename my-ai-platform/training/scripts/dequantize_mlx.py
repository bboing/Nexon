import subprocess
import sys
from pathlib import Path

# 1. 모델 경로 설정
model_name = "meta-llama/Llama-3.1-8B-Instruct"
base_path = Path(__file__).resolve().parent.parent
adapter_path = base_path / "models" / "llama-game-npc-mlx"
save_path = base_path / "models" / "llama-game-npc-mlx-dequantized" 

# 2. [검증 로직 수정] 어댑터가 실제로 있는지 먼저 확인!
if not adapter_path.exists():
    print(f"❌ 어댑터 파일이 없습니다: {adapter_path}")
    sys.exit(1)

# 저장할 폴더는 없으면 생성 (조용히)
save_path.mkdir(parents=True, exist_ok=True)

# 3. 명령어 구성
cmd = [
    sys.executable, "-m", "mlx_lm.fuse",
    "--model", model_name,
    "--adapter-path", str(adapter_path),
    "--save-path", str(save_path),
]

print("📝 실행 명령어:")
print(" ".join(cmd)) 
print("")

# 4. 실행
try:
    # cwd=save_path 삭제: 굳이 빈 폴더 들어가서 실행할 필요 없음. 경로 꼬임 방지.
    result = subprocess.run(cmd, check=True)
    print("\n✅ 어댑터 병합 및 변환 완료!")
    print(f"📂 저장 위치: {save_path}")
except subprocess.CalledProcessError as e:
    print(f"\n❌ 어댑터 병합 실패: {e}")
    sys.exit(1)