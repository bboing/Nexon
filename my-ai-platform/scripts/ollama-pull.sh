#!/bin/bash

# Ollama 모델 다운로드 스크립트

MODEL=$1

if [ -z "$MODEL" ]; then
    echo "🤖 Ollama 모델 다운로드"
    echo "======================================"
    echo ""
    echo "사용법: ./scripts/ollama-pull.sh <모델명>"
    echo ""
    echo "추천 모델:"
    echo "  - llama2          : Llama 2 7B (기본)"
    echo "  - llama2:13b      : Llama 2 13B (더 크고 정확)"
    echo "  - mistral         : Mistral 7B (빠르고 효율적)"
    echo "  - codellama       : Code Llama (코딩용)"
    echo "  - gemma:2b        : Gemma 2B (경량)"
    echo "  - qwen2.5:7b      : Qwen 2.5 7B (다국어 강화)"
    echo ""
    echo "전체 모델 목록: https://ollama.ai/library"
    exit 1
fi

cd "$(dirname "$0")/.."

echo "🤖 Ollama 모델 다운로드: $MODEL"
echo "======================================"

# Ollama 컨테이너 실행 확인
if ! docker-compose ps ollama | grep -q "Up"; then
    echo "❌ Ollama 서비스가 실행되지 않았습니다."
    echo "먼저 서비스를 시작하세요: ./scripts/start-core.sh"
    exit 1
fi

echo ""
echo "📥 모델 다운로드 중... (시간이 걸릴 수 있습니다)"
docker exec -it ai-ollama ollama pull "$MODEL"

echo ""
echo "✅ 다운로드 완료!"
echo ""
echo "🧪 테스트:"
echo "   docker exec -it ai-ollama ollama run $MODEL '안녕하세요'"
echo ""
echo "💡 다운로드된 모델 목록:"
docker exec ai-ollama ollama list

