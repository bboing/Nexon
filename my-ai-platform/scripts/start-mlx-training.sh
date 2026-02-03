#!/bin/bash

set -e

# 스크립트가 어느 위치에 있든 training/ 디렉토리로 이동
cd "$(dirname "$0")/../training"

echo "🍎 Apple MLX 파인튜닝 환경 시작"
echo "================================"

# Mac 확인
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 이 스크립트는 Mac에서만 실행 가능합니다"
    exit 1
fi

# Apple Silicon 확인
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    echo "⚠️  경고: Apple Silicon (M1/M2/M3/M4/M5)이 아닙니다"
    echo "   Intel Mac에서는 성능이 느릴 수 있습니다"
fi

echo "✅ 시스템: macOS ($(uname -m))"
echo ""

# 가상환경 확인
if [ ! -d "mlx-env" ]; then
    echo "📦 MLX 가상환경 생성 중..."
    python3 -m venv mlx-env
    
    echo "📦 MLX 패키지 설치 중..."
    source mlx-env/bin/activate
    pip install --upgrade pip -q
    echo "✅ 설치 완료!"
else
    echo "✅ MLX 가상환경 존재"
    source mlx-env/bin/activate
    echo "✅ MLX 가상환경 활성화"
fi

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
else
    pip install requirements.txt -q
fi

if [ ! -d "llama.cpp" ]; then
    echo "📦 llama.cpp 설치 중..."
    git clone https://github.com/ggerganov/llama.cpp.git
    cd llama.cpp
    make -j$(sysctl -n hw.logicalcpu)
    cd ..
    echo "✅ llama.cpp 설치 완료!"
else 
    echo "✅ llama.cpp 존재"
fi


echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 MLX 파인튜닝 실행_finetune_mlx.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 파인튜닝 실행
python scripts/finetune_mlx.py


echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 양자화 해제_dequantize_mlx.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python scripts/convert_to_gguf.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 GGUF 변환_convert_to_gguf.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python scripts/convert_to_gguf.py


echo "✅ 모든 작업 완료!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Ollama 모델 등록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ollama create llama-game-npc -f models/Modelfile

echo "✅ Ollama 모델 등록 완료!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "local Ollama 모델 실행해서 테스트 해보세유"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "/opt/homebrew/bin/ollama에 있어요. list ollama 먼저 처보고 maple_npc 없으면 create maple_npc -f $PATH_TO_MODERLFILE/Modelfile 실행해보세요."