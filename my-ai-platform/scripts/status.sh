#!/bin/bash

# 서비스 상태 확인 스크립트 (LangChain + Langfuse 포함)

cd "$(dirname "$0")/.."

echo "📊 AI 플랫폼 서비스 상태"
echo "======================================"
echo ""

# 통합 스택 컨테이너 상태
echo "🐳 통합 스택 컨테이너:"
docker compose -f docker-compose.integrated.yml ps

echo ""
echo "======================================"

# 각 서비스 헬스체크
echo ""
echo "🔍 서비스 헬스체크:"
echo ""

# LangChain API
echo -n "  LangChain API:  "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:8000)"
else
    echo "❌ 응답 없음"
fi

# Langfuse
echo -n "  Langfuse:       "
if curl -s http://localhost:3000/api/public/health > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:3000)"
else
    echo "❌ 응답 없음"
fi

# Ollama
echo -n "  Ollama:         "
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:11434)"
else
    echo "❌ 응답 없음"
fi

# PostgreSQL (Biz)
echo -n "  PostgreSQL(Biz):"
if docker exec ai-biz-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "✅ 정상 (localhost:5432)"
else
    echo "❌ 응답 없음"
fi

# PostgreSQL (Ops)
echo -n "  PostgreSQL(Ops):"
if docker exec ai-ops-postgres pg_isready -U langfuse > /dev/null 2>&1; then
    echo "✅ 정상 (localhost:5433)"
else
    echo "❌ 응답 없음"
fi

# Milvus
echo -n "  Milvus:         "
if curl -s http://localhost:9092/healthz > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:19530)"
else
    echo "❌ 응답 없음"
fi

# Redis
echo -n "  Redis:          "
if docker exec ai-redis redis-cli -a "${REDIS_PASSWORD:-changeme}" ping > /dev/null 2>&1; then
    echo "✅ 정상 (localhost:6379)"
else
    echo "❌ 응답 없음"
fi

# Neo4j
echo -n "  Neo4j:          "
if curl -s http://localhost:7474 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:7474)"
else
    echo "❌ 응답 없음"
fi

# Open WebUI
echo -n "  Open WebUI:     "
if curl -s http://localhost:8090 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:8090)"
else
    echo "❌ 응답 없음"
fi

echo ""
echo "======================================"

# 리소스 사용량
echo ""
echo "💾 리소스 사용량:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "======================================"

# 디스크 사용량
echo ""
echo "💿 디스크 사용량:"
echo ""
du -sh ollama/models/ 2>/dev/null || echo "  (데이터 디렉토리가 비어있음)"

echo ""
echo "======================================"
echo ""
echo "📍 주요 접속 주소:"
echo "  🤖 LangChain API:     http://localhost:8000/docs"
echo "  💬 Open WebUI:        http://localhost:8090"
echo "  🪢 Langfuse (추적):   http://localhost:3000"
echo "  🌐 Neo4j Browser:     http://localhost:7474"
echo "  🔄 Ollama:            http://localhost:11434"
echo ""
