#!/bin/bash

# AI Platform 통합 스택 시작 스크립트
# LangChain + Langfuse 셀프호스팅

set -e

cd "$(dirname "$0")/.."

echo "🚀 AI Platform 통합 스택 시작..."
echo "LangChain + Langfuse 셀프호스팅"
echo "=========================================="
echo ""

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다."
    if [ -f env.integrated.example ]; then
        echo "   env.integrated.example을 .env로 복사합니다..."
        cp env.integrated.example .env
        echo "✅ .env 파일이 생성되었습니다."
        echo ""
        echo "❗ 중요: 다음 값들을 반드시 변경하세요:"
        echo "   - POSTGRES_PASSWORD"
        echo "   - REDIS_PASSWORD"
        echo "   - LANGFUSE_NEXTAUTH_SECRET (최소 32자)"
        echo "   - LANGFUSE_SALT (최소 32자)"
        echo "   - LANGFUSE_ENCRYPTION_KEY (64자)"
        echo ""
        echo "💡 보안 키 생성: openssl rand -hex 32"
        echo ""
        read -p "Enter를 눌러 계속하거나 Ctrl+C로 중단하세요..." 
    else
        echo "❌ env.integrated.example 파일도 없습니다."
        exit 1
    fi
fi

# Docker 확인
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker가 실행되지 않았습니다. Docker를 시작해주세요."
    exit 1
fi

# echo "📦 1단계: Ollama 확인 (별도 실행)"
# if docker ps | grep -q ollama; then
#     echo "  ✓ Ollama 실행 중"
# elif docker ps -a | grep -q ollama; then
#     echo "  ⚠️  Ollama 컨테이너 존재하지만 중지됨. 시작합니다..."
#     docker start ollama 2>/dev/null || docker compose up -d ollama
# else
#     echo "  ⚠️  Ollama가 없습니다. 시작합니다..."
#     docker compose up -d ollama
# fi

echo ""
echo "📦 1단계: 통합 스택 빌드 및 시작..."
echo "  (예상 시간: 첫 실행 5-10분, 이후 1-2분)"
docker compose -f docker-compose.integrated.yml up -d --build

echo ""
echo "⏳ 2단계: 서비스 초기화 대기 중..."
sleep 20

echo ""
echo "✅ 서비스 헬스 체크:"
echo ""

# Ollama
echo -n "  Ollama:         "
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "✅ http://localhost:11434"
else
    echo "❌ 응답 없음"
fi

# PostgreSQL
echo -n "  PostgreSQL:     "
if docker exec ai-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "✅ localhost:5432"
else
    echo "❌ 응답 없음"
fi

# Redis
echo -n "  Redis:          "
if docker exec ai-redis redis-cli -a "${REDIS_PASSWORD:-changeme}" ping > /dev/null 2>&1; then
    echo "✅ localhost:6379"
else
    echo "❌ 응답 없음"
fi

# Clickhouse
echo -n "  Clickhouse:     "
if curl -s http://localhost:8123/ping > /dev/null 2>&1; then
    echo "✅ localhost:8123"
else
    echo "❌ 응답 없음 (초기화 중...)"
fi

# Milvus
echo -n "  Milvus:         "
if curl -s http://localhost:9092/healthz > /dev/null 2>&1; then
    echo "✅ localhost:19530"
else
    echo "❌ 응답 없음 (초기화 중...)"
fi

# LangChain API
echo -n "  LangChain API:  "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ http://localhost:8000"
else
    echo "❌ 응답 없음 (초기화 중...)"
fi

# Langfuse
echo -n "  Langfuse:       "
if curl -s http://localhost:3000/api/public/health > /dev/null 2>&1; then
    echo "✅ http://localhost:3000"
else
    echo "❌ 응답 없음 (초기화 중...)"
fi

echo ""
echo "🎉 AI Platform 통합 스택 시작 완료!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 주요 서비스 접속:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 LangChain API:     http://localhost:8000/docs"
echo "  💬 Open WebUI:        http://localhost:8090 ⭐"
echo "  🪢 Langfuse (추적):   http://localhost:3000"
echo "  🌐 Neo4j Browser:     http://localhost:7474"
echo "  📦 MinIO (Milvus):    http://localhost:9001"
echo "  📦 MinIO (Langfuse):  http://localhost:9093"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  중요: Langfuse 초기 설정"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. http://localhost:3000 접속하여 계정 생성"
echo "  2. Settings → API Keys에서 Public/Secret Key 생성"
echo "  3. .env 파일에 LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY 추가"
echo "  4. docker compose -f docker-compose.integrated.yml restart langchain-api"
echo ""
echo "📖 NPC 대화 테스트:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo '  curl -X POST http://localhost:8000/api/npc/chat \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"npc_name": "밍밍부인", "message": "안녕하세요!"}'"'"
echo ""
echo "📝 로그 확인:"
echo "  docker compose -f docker-compose.integrated.yml logs -f"
echo ""
echo "🛑 종료:"
echo "  docker compose -f docker-compose.integrated.yml down"
echo ""
echo "📚 상세 가이드:"
echo "  cat INTEGRATED_SETUP.md"
echo ""
