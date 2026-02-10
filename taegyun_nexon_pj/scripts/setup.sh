#!/bin/bash
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'


# 1. 에러 발생 시 즉시 중단 및 루트 경로 설정
set -e
SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
ROOT_DIR="$( cd "$( dirname "$SCRIPT_PATH" )/.." && pwd )"

echo "=========================================="
echo "🚀 AI Platform Setup (Nexon Project)"
echo "📂 Root: $ROOT_DIR"
echo "=========================================="

# [함수] 서비스 대기 로직
wait_for_service() {
    local host="$1"
    local port="$2"
    local name="$3"
    local timeout=60
    local counter=0

    echo -n "   ⏳ $name ($port) 연결 확인 중"
    while ! nc -z "$host" "$port" > /dev/null 2>&1; do
        sleep 1
        echo -n "."
        ((counter++))
        if [ $counter -gt $timeout ]; then
            echo -e "\n   ❌ $name 대기 시간 초과 (60초)"
            exit 1
        fi
    done
    echo -e "\n   ✅ $name 연결 성공!"
}

# 1️⃣ 사전 의존성 및 Docker 상태 확인
echo -e "\n1️⃣ 시스템 환경 확인 중..."

if ! command -v python3 &> /dev/null; then echo "❌ Python3 미설치"; exit 1; fi
if ! command -v docker &> /dev/null; then echo "❌ Docker 미설치"; exit 1; fi

# Docker 실행 여부 확인 및 Mac 자동 실행
if ! docker info &> /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   🐳 Docker Desktop 실행 중..."
        open -a Docker
        sleep 20
    else
        echo "   ❌ Docker가 실행 중이지 않습니다."; exit 1
    fi
fi
echo "   ✅ Python & Docker 준비 완료"

# 2️⃣ 환경 변수(.env) 설정
echo -e "\n2️⃣ 환경 변수 설정..."
if [ ! -f "${ROOT_DIR}/.env" ]; then
    if [ -f "${ROOT_DIR}/.env.example" ]; then
        cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
        echo "   📋 .env 파일 생성 완료 (설정을 확인하세요)"
    else
        echo "   ❌ .env.example 파일이 없습니다."; exit 1
    fi
else
    echo "   ✅ .env 파일 확인 완료"
fi

# 3️⃣ 인프라 가동 (Docker Compose)
echo -e "\n3️⃣ Docker 컨테이너 가동..."
docker-compose -f "${ROOT_DIR}/docker-compose.yml" up -d

wait_for_service "localhost" 5432 "Postgres"
wait_for_service "localhost" 7687 "Neo4j"
wait_for_service "localhost" 19530 "Milvus"

echo "   ⏳ 서비스 준비 중... (20초 대기)"
sleep 20

# 4️⃣ 가상환경 및 라이브러리 설치
echo -e "\n4️⃣ Python 가상환경 설정..."
if [ ! -d "${ROOT_DIR}/nexon_venv" ]; then
    python3 -m venv "${ROOT_DIR}/nexon_venv"
fi
source "${ROOT_DIR}/nexon_venv/bin/activate"

echo "   의존성 라이브러리 설치 중..."
pip install --upgrade pip > /dev/null
# 통합 requirements.txt 사용 (langchain_app + streamlit_app + scripts 전체 포함)
pip install -r "${ROOT_DIR}/requirements.txt" > /dev/null

# 5️⃣ 데이터베이스 초기화 및 시딩 (중요 순서!)
echo -e "\n5️⃣ 데이터 지식 구조화 시작..."

echo "   [1/3] Postgres 데이터 임포트..."
python3 "${ROOT_DIR}/scripts/import_data.py" "${ROOT_DIR}/training/data/input_data/maple_data.json"

echo "   [2/3] Milvus 벡터 인덱싱..."
python3 "${ROOT_DIR}/scripts/sync_to_milvus.py"

echo "   [3/3] Neo4j 그래프 관계 구축..."
python3 "${ROOT_DIR}/scripts/sync_to_neo4j.py"

echo "   ✅ 모든 지식 베이스 구축 완료!"

# 6️⃣ Ollama 상태 확인
echo -e "\n6️⃣ Ollama 서버 확인..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ⚠️ Ollama 실행 안 됨 (별도로 실행 필요)"
else
    echo "   ✅ Ollama 실행 중"
fi

# echo -e "\n=========================================="
# echo "🎉 Setup 완료되었습니다."
# echo "가상환경에 세팅되어 있으니, local 터미널에 아래의 명령어로 가상환경 접속해주세요"
# echo "source nexon_venv/bin/activate"
# echo "테스트 할 파일은 scripts/test_answer_generator.py 입니다. 실행 방법은 다음과 같습니다."
# echo " 터미널에 > python test_answer_generator.py "question" < 치시면 됩니다.(question에 쌍따옴표 붙여주세요!)"
# echo " 감사합니다. "
# echo "=========================================="

echo -e "\n${GREEN}==========================================================${NC}"
echo -e "${GREEN}🎉 AI Platform Infrastructure Setup Completed Successfully${NC}"
echo -e "${GREEN}==========================================================${NC}"

echo -e "\n${CYAN}1. Virtual Environment (가상환경) 활성화${NC}"
echo -e "   의존성 격리를 위해 아래 명령어로 가상환경에 접속하세요:"
echo -e "   ${YELLOW}source nexon_venv/bin/activate${NC}"

echo -e "\n${CYAN}2. RAG Engine 검증 테스트${NC}"
echo -e "   구축된 지식 베이스를 바탕으로 AI 답변을 생성합니다."
echo -e "   ${YELLOW}예시: python scripts/test_answer_generator.py \"도적 전직 방법 알려줘\"${NC}"
echo -e "   ${YELLOW}python scripts/test_answer_generator.py${NC} 만 실행하셔도 됩니다."

echo -e "\n${CYAN}3. 데이터셋 및 프로젝트 참고사항${NC}"
echo -e "   * ${YELLOW}Dataset Location:${NC} ${ROOT_DIR}/training/data/input_data/maple_data.json"
echo -e "   * 본 데이터는 RAG 파이프라인의 ${YELLOW}기술적 검증을 위해 구성된 샘플 데이터셋${NC}입니다."
echo -e "   * 실제 게임 정보와 차이가 있을 수 있으며, 아키텍처 테스트 용도로 최적화되어 있습니다."

echo -e "\n${CYAN}4. Infra 서비스 접속 정보 (Local)${NC}"
echo -e "   ┌────────────┬─────────────────────────────┬────────────────────────────────┐"
echo -e "   │ Service    │ Endpoint                    │ Credentials                    │"
echo -e "   ├────────────┼─────────────────────────────┼────────────────────────────────┤"
echo -e "   │ PostgreSQL │ localhost:5432              │ .env 설정 참조                 │"
echo -e "   │ Milvus UI  │ http://localhost:8000       │ minioadmin / nexonJjang67!     │"
echo -e "   │ Neo4j UI   │ http://localhost:7474       │ neo4j / nexonJjang67!          │"
echo -e "   └────────────┴─────────────────────────────┴────────────────────────────────┘"
echo -e "   * 상세 접속 정보는 프로젝트 루트의 .env 파일에서 관리됩니다."

echo -e "\n${GREEN}감사합니다. 추가 문의는 프로젝트 README.md를 참조해주세요.${NC}"
echo -e "${GREEN}==========================================================${NC}\n"