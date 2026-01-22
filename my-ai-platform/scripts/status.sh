#!/bin/bash

# 서비스 상태 확인 스크립트 (LangChain + Langfuse 포함)

cd "$(dirname "$0")/.."

echo "📊 AI 플랫폼 서비스 상태"
echo "======================================"
echo ""

# 기본 컨테이너 상태
echo "🐳 기본 인프라 컨테이너:"
docker compose ps

# LangChain 스택 컨테이너 상태
if [ -f docker-compose.langchain.yml ]; then
    echo ""
    echo "🐳 LangChain 스택 컨테이너:"
    docker compose -f docker-compose.langchain.yml ps
fi

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
if curl -s http://localhost:3001/api/public/health > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:3001)"
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

# PostgreSQL
echo -n "  PostgreSQL:     "
if docker exec ai-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "✅ 정상 (localhost:5432)"
else
    echo "❌ 응답 없음"
fi

# Milvus
echo -n "  Milvus:         "
if curl -s http://localhost:9091/healthz > /dev/null 2>&1; then
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

# Attu (Milvus UI)
echo -n "  Attu:           "
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:8080)"
else
    echo "❌ 응답 없음"
fi

# n8n
echo -n "  n8n:            "
if curl -s http://localhost:5678 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:5678)"
else
    echo "❌ 응답 없음"
fi

# Grafana
echo -n "  Grafana:        "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:3000)"
else
    echo "❌ 응답 없음"
fi

# Prometheus
echo -n "  Prometheus:     "
if curl -s http://localhost:9090 > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:9090)"
else
    echo "❌ 응답 없음"
fi

# Loki
echo -n "  Loki:           "
if curl -s http://localhost:3100/ready > /dev/null 2>&1; then
    echo "✅ 정상 (http://localhost:3100)"
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
du -sh ollama/models/ n8n/data/ 2>/dev/null || echo "  (데이터 디렉토리가 비어있음)"

echo ""
echo "======================================"
echo ""
echo "📍 주요 접속 주소:"
echo "  🤖 LangChain API:     http://localhost:8000/docs"
echo "  🪢 Langfuse (추적):   http://localhost:3001"
echo "  🗄️  Attu (Milvus UI): http://localhost:8080"
echo "  📊 Grafana:           http://localhost:3000"
echo "  🔄 n8n:               http://localhost:5678"
echo ""
