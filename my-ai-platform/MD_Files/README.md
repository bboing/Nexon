# 🚀 AI Platform - 통합 AI 인프라 스택

Docker Compose 기반의 완전한 AI 플랫폼 스택입니다. n8n 워크플로우 자동화, Ollama LLM, 그리고 Prometheus + Loki + Grafana 모니터링 스택을 통합하여 제공합니다.

## 📦 포함된 서비스

| 서비스 | 용도 | 포트 | 접속 URL |
|--------|------|------|----------|
| **n8n** | 워크플로우 자동화 | 5678 | http://localhost:5678 |
| **Ollama** | LLM 모델 서버 | 11434 | http://localhost:11434 |
| **Grafana** | 모니터링 대시보드 | 3000 | http://localhost:3000 |
| **Prometheus** | 메트릭 수집 | 9090 | http://localhost:9090 |
| **Loki** | 로그 저장소 | 3100 | http://localhost:3100 |
| **Promtail** | 로그 수집 | - | - |
| **Nginx** | 리버스 프록시 | 80/443 | http://localhost |

## 🛠️ 사전 요구사항

- Docker Engine 20.10+
- Docker Compose V2+
- 최소 8GB RAM (권장: 16GB+)
- GPU (선택사항, Ollama LLM 성능 향상)
- 디스크 공간 최소 20GB (LLM 모델 용량에 따라 더 필요)

## 🚀 빠른 시작

### 1. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 비밀번호 변경 (중요!)
nano .env
```

**반드시 변경해야 할 항목:**
- `N8N_PASSWORD`: n8n 관리자 비밀번호
- `GRAFANA_PASSWORD`: Grafana 관리자 비밀번호

### 2. 플랫폼 시작

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스만 시작
docker-compose up -d n8n ollama grafana
```

### 3. 서비스 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 서비스 상태 확인
curl http://localhost:11434  # Ollama
curl http://localhost:5678   # n8n
curl http://localhost:3000   # Grafana
```

## 📖 서비스별 사용 가이드

### 🤖 Ollama (LLM 모델)

Ollama는 로컬에서 LLM 모델을 실행할 수 있게 해주는 도구입니다.

```bash
# 컨테이너 접속
docker exec -it ai-ollama bash

# 모델 다운로드 및 실행
ollama pull llama2           # Llama 2 (7B)
ollama pull mistral          # Mistral (7B)
ollama pull codellama        # Code Llama (코딩용)
ollama pull llama2:13b       # Llama 2 13B (더 큰 모델)

# 모델 테스트
ollama run llama2 "안녕하세요"

# API로 사용
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Why is the sky blue?"
}'
```

**모델 저장 위치:** `./ollama/models/`

### 🔄 n8n (워크플로우 자동화)

1. 웹 브라우저에서 http://localhost:5678 접속
2. `.env` 파일의 계정으로 로그인
   - 사용자명: `admin` (기본값)
   - 비밀번호: `.env`에서 설정한 `N8N_PASSWORD`
3. 워크플로우 생성 및 실행

**n8n + Ollama 통합 예시:**
- HTTP Request 노드로 Ollama API 호출
- Webhook 트리거로 외부 이벤트 수신
- 자동화된 AI 응답 파이프라인 구축

**데이터 저장 위치:** `./n8n/data/`

### 📊 Grafana (모니터링 대시보드)

1. http://localhost:3000 접속
2. 로그인
   - 사용자명: `admin` (기본값)
   - 비밀번호: `.env`에서 설정한 `GRAFANA_PASSWORD`

**데이터 소스 추가:**
1. Configuration → Data Sources
2. Prometheus 추가:
   - URL: `http://prometheus:9090`
3. Loki 추가:
   - URL: `http://loki:3100`

**추천 대시보드:**
- Node Exporter Full (ID: 1860) - 시스템 메트릭
- Docker Container & Host Metrics (ID: 179) - 컨테이너 메트릭
- Loki Dashboard (ID: 13639) - 로그 분석

### 📈 Prometheus (메트릭 수집)

- 웹 UI: http://localhost:9090
- 설정 파일: `./prometheus/prometheus.yml`
- 자동으로 모든 서비스의 메트릭 수집

### 📝 Loki + Promtail (로그 관리)

- Loki: 로그 저장소
- Promtail: 자동으로 Docker 컨테이너 로그 수집
- Grafana에서 로그 조회 및 분석

## 🌐 Nginx 리버스 프록시

`/etc/hosts` 파일에 추가하여 서브도메인으로 접근:

```bash
# /etc/hosts 파일 편집
sudo nano /etc/hosts

# 다음 줄 추가
127.0.0.1 n8n.localhost
127.0.0.1 grafana.localhost
127.0.0.1 ollama.localhost
127.0.0.1 prometheus.localhost
```

그 후:
- http://n8n.localhost → n8n
- http://grafana.localhost → Grafana
- http://ollama.localhost → Ollama API
- http://prometheus.localhost → Prometheus

## 🔧 관리 명령어

### 기본 관리

```bash
# 모든 서비스 중지
docker-compose down

# 데이터 포함 완전 삭제
docker-compose down -v

# 서비스 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart ollama

# 로그 확인
docker-compose logs -f [서비스명]
```

### 리소스 확인

```bash
# 디스크 사용량
docker system df

# 컨테이너 리소스 사용량
docker stats

# 볼륨 확인
docker volume ls | grep ai-platform
```

### 백업

```bash
# n8n 데이터 백업
tar -czf n8n-backup-$(date +%Y%m%d).tar.gz ./n8n/data/

# Ollama 모델 백업
tar -czf ollama-backup-$(date +%Y%m%d).tar.gz ./ollama/models/

# Grafana 설정 백업
docker exec ai-grafana grafana-cli admin reset-admin-password --homepath "/usr/share/grafana" admin
```

## 🐛 문제 해결

### Ollama가 시작되지 않음

```bash
# GPU 없이 실행 (docker-compose.yml에서 GPU 부분 제거)
docker-compose up -d ollama

# 로그 확인
docker-compose logs ollama
```

### n8n에 접속할 수 없음

```bash
# 포트 충돌 확인
netstat -tuln | grep 5678

# 컨테이너 재시작
docker-compose restart n8n
```

### 디스크 공간 부족

```bash
# 사용하지 않는 Docker 리소스 정리
docker system prune -a

# 오래된 로그 삭제
docker-compose logs --tail=0 -f
```

### Prometheus 메트릭이 수집되지 않음

```bash
# Prometheus 설정 리로드
docker exec ai-prometheus kill -HUP 1

# 타겟 상태 확인
curl http://localhost:9090/api/v1/targets
```

## 📊 성능 최적화

### GPU 사용 (Ollama)

NVIDIA GPU가 있는 경우:

```bash
# NVIDIA Container Toolkit 설치
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 메모리 제한 설정

`docker-compose.yml`에 추가:

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
```

## 🔒 보안 권장사항

1. **비밀번호 변경**: `.env` 파일의 모든 기본 비밀번호 변경
2. **방화벽 설정**: 외부 접근이 필요 없는 포트는 방화벽으로 차단
3. **SSL/TLS**: 프로덕션 환경에서는 Nginx에 SSL 인증서 설정
4. **.env 보호**: `.env` 파일을 git에 커밋하지 말 것
5. **정기 업데이트**: 보안 패치를 위해 이미지 정기 업데이트

```bash
# 이미지 업데이트
docker-compose pull
docker-compose up -d
```

## 📁 디렉토리 구조

```
my-ai-platform/
├── docker-compose.yml       # 서비스 정의
├── .env.example            # 환경 변수 템플릿
├── .env                    # 실제 환경 변수 (생성 필요)
├── README.md               # 이 문서
├── nginx/
│   └── nginx.conf          # Nginx 설정
├── n8n/
│   └── data/               # n8n 워크플로우 데이터
├── ollama/
│   └── models/             # LLM 모델 저장소
├── prometheus/
│   └── prometheus.yml      # 메트릭 수집 설정
├── promtail/
│   └── config.yml          # 로그 수집 설정
└── loki/
    └── config.yml          # 로그 저장 설정
```

## 🤝 기여 및 지원

문제가 발생하거나 개선 사항이 있다면:
1. GitHub Issues에 보고
2. Pull Request 제출
3. 문서 개선 제안

## 📝 라이선스

이 프로젝트는 각 컴포넌트의 라이선스를 따릅니다:
- n8n: Sustainable Use License
- Ollama: MIT License
- Grafana: AGPL-3.0
- Prometheus: Apache 2.0
- Loki: AGPL-3.0

## 🔗 유용한 링크

- [n8n 문서](https://docs.n8n.io/)
- [Ollama 모델 라이브러리](https://ollama.ai/library)
- [Grafana 대시보드](https://grafana.com/grafana/dashboards/)
- [Prometheus 쿼리 가이드](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Docker Compose 문서](https://docs.docker.com/compose/)

---

**즐거운 AI 개발 되세요! 🎉**

