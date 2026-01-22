# 🔧 .env 파일 설정하기

## 📝 변수 정리 및 설명

### 🎯 필수 변수 (반드시 설정)

```bash
N8N_USER              # n8n 로그인 ID
N8N_PASSWORD          # n8n 로그인 비밀번호 ⚠️ 반드시 변경!
GRAFANA_USER          # Grafana 로그인 ID
GRAFANA_PASSWORD      # Grafana 로그인 비밀번호 ⚠️ 반드시 변경!
```

### 🔧 선택 변수 (기본값 있음)

**포트 설정**
```bash
NGINX_PORT=80         # Nginx HTTP 포트
NGINX_SSL_PORT=443    # Nginx HTTPS 포트
N8N_PORT=5678         # n8n 서비스 포트
OLLAMA_PORT=11434     # Ollama API 포트
GRAFANA_PORT=3000     # Grafana 웹 UI 포트
PROMETHEUS_PORT=9090  # Prometheus 웹 UI 포트
LOKI_PORT=3100        # Loki API 포트
```

**버전 설정**
```bash
N8N_VERSION=latest
OLLAMA_VERSION=latest
GRAFANA_VERSION=latest
PROMETHEUS_VERSION=latest
LOKI_VERSION=latest
PROMTAIL_VERSION=latest
```

**기타 설정**
```bash
N8N_HOST=localhost
N8N_WEBHOOK_URL=http://localhost:5678/
```

## 🚀 빠른 설정 방법

### 방법 1: 전체 설정 (권장)

```bash
# 1. 예제 파일 복사
cp env.example .env

# 2. 에디터로 열기
nano .env

# 3. 비밀번호만 수정
N8N_PASSWORD=강력한비밀번호123!
GRAFANA_PASSWORD=강력한비밀번호456!

# 4. 저장하고 종료 (Ctrl+X, Y, Enter)
```

### 방법 2: 최소 설정

```bash
# 필수 항목만 있는 최소 버전 사용
cp env.minimal .env
nano .env
```

### 방법 3: 직접 생성

```bash
cat > .env << 'ENVFILE'
# 보안 설정
N8N_USER=admin
N8N_PASSWORD=YourStrongPassword123!
GRAFANA_USER=admin
GRAFANA_PASSWORD=YourStrongPassword456!
ENVFILE
```

## 📋 설정 예시

### 🏠 로컬 개발용

```env
# .env
N8N_USER=admin
N8N_PASSWORD=dev123456
GRAFANA_USER=admin
GRAFANA_PASSWORD=dev789012
```

### 🏢 프로덕션용

```env
# .env
N8N_USER=admin_prod
N8N_PASSWORD=V3ry$tr0ng!P@ssw0rd#2024
GRAFANA_USER=admin_prod
GRAFANA_PASSWORD=An0th3r$tr0ng!P@ss#2024

# 버전 고정
N8N_VERSION=1.19.0
OLLAMA_VERSION=0.1.17
GRAFANA_VERSION=10.2.0
```

### 🔀 포트 변경이 필요한 경우

```env
# 다른 서비스와 충돌 시
N8N_PORT=15678
GRAFANA_PORT=13000
OLLAMA_PORT=21434
```

## ✅ 설정 확인

```bash
# .env 파일 확인
cat .env

# Docker Compose가 읽는 값 확인
docker-compose config | grep -A 5 environment

# 테스트
./scripts/start-all.sh
./scripts/status.sh
```

## 🔒 보안 체크리스트

- [ ] `.env` 파일 생성 완료
- [ ] `N8N_PASSWORD` 기본값에서 변경
- [ ] `GRAFANA_PASSWORD` 기본값에서 변경
- [ ] 비밀번호 최소 12자 이상 사용
- [ ] `.gitignore`에 `.env` 포함 확인
- [ ] 비밀번호를 안전하게 보관

## 🆘 문제 해결

### .env 파일이 인식되지 않는 경우

```bash
# 위치 확인
pwd  # my-ai-platform 디렉토리에 있어야 함
ls -la .env  # 파일 존재 확인

# 재시작
docker-compose down
docker-compose up -d
```

### 비밀번호가 적용되지 않는 경우

```bash
# 컨테이너 완전 재생성
docker-compose down -v
docker-compose up -d
```

## 📚 더 자세한 정보

전체 환경 변수 가이드: `ENV_GUIDE.md` 참고
