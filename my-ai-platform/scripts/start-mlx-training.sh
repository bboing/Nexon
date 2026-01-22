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
echo "🚀 MLX 파인튜닝 실행"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 파인튜닝 실행
python scripts/finetune_mlx.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 학습된 모델 위치:"
echo "   models/llama-game-npc-mlx/"
echo ""
echo "🎯 다음 단계:"
echo "   1. models/ 디렉토리에서 adapters.safetensors 확인"
echo "   2. 더 많은 데이터로 재학습"
echo "   3. Ollama로 배포"
echo ""
