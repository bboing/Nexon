#!/bin/bash

# 백업 스크립트

cd "$(dirname "$0")/.."

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ai-platform-backup-${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "💾 AI 플랫폼 데이터 백업 시작..."
echo "======================================"

# 백업할 디렉토리 목록
echo "📦 백업 중:"
echo "  - n8n 워크플로우 데이터"
echo "  - Ollama 모델 파일"
echo "  - 설정 파일"
echo ""

# 백업 생성
tar -czf "$BACKUP_FILE" \
    --exclude='node_modules' \
    --exclude='.git' \
    n8n/data/ \
    ollama/models/ \
    .env.example \
    docker-compose.yml \
    nginx/ \
    prometheus/ \
    promtail/ \
    loki/ \
    2>/dev/null

BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)

echo ""
echo "✅ 백업 완료!"
echo ""
echo "📁 백업 파일: $BACKUP_FILE"
echo "📏 크기: $BACKUP_SIZE"
echo ""
echo "💡 복원 방법:"
echo "   tar -xzf $BACKUP_FILE"

