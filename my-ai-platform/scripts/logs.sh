#!/bin/bash

# 로그 확인 스크립트

cd "$(dirname "$0")/.."

SERVICE=$1

if [ -z "$SERVICE" ]; then
    echo "📝 전체 서비스 로그 확인 (Ctrl+C로 종료)"
    echo "========================================"
    echo ""
    docker-compose logs -f
else
    echo "📝 $SERVICE 로그 확인 (Ctrl+C로 종료)"
    echo "========================================"
    echo ""
    docker-compose logs -f "$SERVICE"
fi

