#!/bin/bash

# 전체 정리 스크립트 (데이터 포함 삭제)

cd "$(dirname "$0")/.."

echo "⚠️  경고: 모든 데이터가 삭제됩니다!"
echo "======================================"
echo ""
echo "다음 항목이 삭제됩니다:"
echo "  - 모든 컨테이너"
echo "  - 모든 볼륨 (데이터 포함)"
echo "  - n8n 워크플로우 데이터"
echo "  - Ollama 모델 파일"
echo "  - Grafana 대시보드 설정"
echo ""
read -p "계속하시겠습니까? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "취소되었습니다."
    exit 0
fi

echo ""
echo "🧹 정리 시작..."

# 컨테이너 및 볼륨 삭제
docker-compose down -v

# 로컬 데이터 삭제
echo "📂 로컬 데이터 삭제..."
rm -rf n8n/data/*
rm -rf ollama/models/*

# .gitkeep 복원
touch n8n/data/.gitkeep
touch ollama/models/.gitkeep

echo ""
echo "✅ 정리 완료!"
echo ""
echo "💡 새로 시작하려면: ./scripts/start-all.sh"

