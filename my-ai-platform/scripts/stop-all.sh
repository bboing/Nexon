#!/bin/bash

# 전체 AI 플랫폼 중지 스크립트 (LangChain + Langfuse 포함)

set -e

cd "$(dirname "$0")/.."

echo "🛑 AI 플랫폼 전체 서비스 중지..."
echo "================================"

# LangChain 스택 중지
if [ -f docker-compose.langchain.yml ]; then
    echo "📦 LangChain 스택 중지 중..."
    docker compose -f docker-compose.integrated.yml down
fi

# 기본 인프라 중지
echo "📦 기본 인프라 중지 중..."
docker compose -f docker-compose.integrated.yml down

echo ""
echo "✅ 모든 서비스가 중지되었습니다."
echo ""
echo "💡 TIP:"
echo "  - 재시작: ./scripts/start-all.sh"
echo "  - 데이터 포함 삭제: docker compose down -v && docker compose -f docker-compose.integrated.yml down -v"
echo "  - 로그 정리: ./scripts/cleanup.sh"

