#!/bin/bash

# 이미지 업데이트 스크립트

cd "$(dirname "$0")/.."

echo "🔄 Docker 이미지 업데이트"
echo "======================================"
echo ""

# 현재 실행 중인지 확인
RUNNING=$(docker-compose ps -q)

if [ -n "$RUNNING" ]; then
    echo "⚠️  서비스가 실행 중입니다."
    read -p "중지하고 업데이트하시겠습니까? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "취소되었습니다."
        exit 0
    fi
    
    echo ""
    echo "🛑 서비스 중지 중..."
    docker-compose down
fi

echo ""
echo "📥 최신 이미지 다운로드 중..."
docker-compose pull

echo ""
echo "🚀 서비스 재시작 중..."
docker-compose up -d

echo ""
echo "⏳ 서비스 시작 대기 중... (10초)"
sleep 10

echo ""
echo "✅ 업데이트 완료!"
echo ""
docker-compose ps

echo ""
echo "💡 로그 확인: ./scripts/logs.sh"

