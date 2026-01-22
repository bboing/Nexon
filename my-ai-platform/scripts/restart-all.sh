#!/bin/bash

# 전체 AI 플랫폼 재시작 스크립트

set -e

cd "$(dirname "$0")/.."

echo "🔄 AI 플랫폼 재시작 중..."
echo "================================"

# 중지
echo "1️⃣ 서비스 중지..."
docker-compose down

echo ""
echo "2️⃣ 서비스 시작..."
docker-compose up -d

# 상태 확인
echo ""
echo "⏳ 서비스 시작 대기 중... (10초)"
sleep 10

echo ""
echo "✅ 서비스 상태:"
docker-compose ps

echo ""
echo "🎉 재시작 완료!"

