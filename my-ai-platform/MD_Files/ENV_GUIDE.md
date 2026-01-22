# 🔧 환경 변수 설정 가이드

## 📋 변수 목록

### 🔐 보안 설정 (필수)

| 변수명 | 기본값 | 설명 | 비고 |
|--------|--------|------|------|
| `N8N_USER` | admin | n8n 관리자 ID | **필수 변경** |
| `N8N_PASSWORD` | - | n8n 관리자 비밀번호 | **필수 변경** |
| `GRAFANA_USER` | admin | Grafana 관리자 ID | **필수 변경** |
| `GRAFANA_PASSWORD` | - | Grafana 관리자 비밀번호 | **필수 변경** |

### 🌐 Nginx 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `NGINX_PORT` | 80 | HTTP 포트 | 선택 |
| `NGINX_SSL_PORT` | 443 | HTTPS 포트 | 선택 |

### 🔄 n8n 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `N8N_VERSION` | latest | 이미지 버전 | 선택 |
| `N8N_PORT` | 5678 | 서비스 포트 | 선택 |
| `N8N_HOST` | localhost | 호스트명 | 선택 |
| `N8N_WEBHOOK_URL` | http://localhost:5678/ | 웹훅 URL | 선택 |

### 🤖 Ollama 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `OLLAMA_VERSION` | latest | 이미지 버전 | 선택 |
| `OLLAMA_PORT` | 11434 | API 포트 | 선택 |

### 📊 Prometheus 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `PROMETHEUS_VERSION` | latest | 이미지 버전 | 선택 |
| `PROMETHEUS_PORT` | 9090 | 웹 UI 포트 | 선택 |

### 📝 Loki 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `LOKI_VERSION` | latest | 이미지 버전 | 선택 |
| `LOKI_PORT` | 3100 | API 포트 | 선택 |

### 🔍 Promtail 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `PROMTAIL_VERSION` | latest | 이미지 버전 | 선택 |

### 📈 Grafana 설정

| 변수명 | 기본값 | 설명 | 변경 필요 |
|--------|--------|------|----------|
| `GRAFANA_VERSION` | latest | 이미지 버전 | 선택 |
| `GRAFANA_PORT` | 3000 | 웹 UI 포트 | 선택 |

## 🚀 빠른 시작

### 1️⃣ 기본 설정 (권장)

```bash
# .env 파일 생성
cp .env.example .env

# 비밀번호만 수정
nano .env
```

**수정할 항목:**
```env
N8N_PASSWORD=강력한비밀번호123!@#
GRAFANA_PASSWORD=강력한비밀번호456!@#
```

### 2️⃣ 최소 설정

```bash
# 템플릿 사용 (필수 항목만)
cp .env.template .env
nano .env
```

## 📝 시나리오별 설정

### 🏠 로컬 개발 환경

```env
# .env
N8N_USER=admin
N8N_PASSWORD=devpass123
GRAFANA_USER=admin
GRAFANA_PASSWORD=devpass456

# 모든 버전 latest 사용
N8N_VERSION=latest
OLLAMA_VERSION=latest
GRAFANA_VERSION=latest
```

### 🏢 프로덕션 환경

```env
# .env
N8N_USER=admin_prod
N8N_PASSWORD=V3ry$tr0ng!P@ssw0rd
GRAFANA_USER=admin_prod
GRAFANA_PASSWORD=An0th3r$tr0ng!P@ss

# 버전 고정 (안정성)
N8N_VERSION=1.19.0
OLLAMA_VERSION=0.1.17
GRAFANA_VERSION=10.2.0
PROMETHEUS_VERSION=v2.48.0
LOKI_VERSION=2.9.0

# 커스텀 도메인
N8N_HOST=n8n.mycompany.com
N8N_WEBHOOK_URL=https://n8n.mycompany.com/
```

### 🔒 포트 충돌 해결

다른 서비스와 포트가 겹치는 경우:

```env
# .env
N8N_PORT=15678        # 5678 대신
OLLAMA_PORT=21434     # 11434 대신
GRAFANA_PORT=13000    # 3000 대신
PROMETHEUS_PORT=19090 # 9090 대신
```

⚠️ **주의:** nginx.conf도 함께 수정해야 합니다!

### 🐳 여러 환경 관리

```bash
# 개발 환경
cp .env.example .env.dev

# 스테이징 환경
cp .env.example .env.staging

# 프로덕션 환경
cp .env.example .env.prod

# 사용 시
cp .env.prod .env
docker-compose up -d
```

## 🔒 보안 베스트 프랙티스

### ✅ 해야 할 것

1. **강력한 비밀번호 사용**
   ```
   최소 12자, 대소문자+숫자+특수문자 조합
   ✅ MyStr0ng!P@ssw0rd#2024
   ❌ admin123
   ```

2. **.gitignore 확인**
   ```bash
   # .gitignore에 반드시 포함
   .env
   .env.local
   .env.*.local
   ```

3. **비밀번호 관리자 사용**
   - 1Password, Bitwarden 등 활용
   - 팀 공유는 안전한 채널만 사용

4. **정기적인 비밀번호 변경**
   ```bash
   # 변경 후 재시작
   nano .env
   docker-compose restart n8n grafana
   ```

### ❌ 하지 말아야 할 것

1. **.env 파일을 Git에 커밋** ⛔
2. **기본 비밀번호 사용** ⛔
3. **평문으로 비밀번호 공유** ⛔
4. **공개 저장소에 .env 업로드** ⛔

## 🧪 설정 검증

### 변수 확인

```bash
# .env 파일 확인
cat .env

# Docker에서 사용되는 값 확인
docker-compose config
```

### 비밀번호 테스트

```bash
# 서비스 시작
docker-compose up -d

# n8n 로그인 테스트
curl -u admin:YOUR_PASSWORD http://localhost:5678

# Grafana 로그인 테스트
curl -u admin:YOUR_PASSWORD http://localhost:3000/api/health
```

## 🆘 문제 해결

### 변수가 적용되지 않는 경우

```bash
# 1. 컨테이너 완전 재생성
docker-compose down
docker-compose up -d

# 2. 캐시 없이 재빌드
docker-compose up -d --force-recreate

# 3. 환경 변수 직접 확인
docker exec ai-n8n env | grep N8N
```

### 포트 충돌

```bash
# 사용 중인 포트 확인
lsof -i :5678
lsof -i :3000

# .env에서 포트 변경 후 재시작
docker-compose down
docker-compose up -d
```

### 비밀번호 분실

```bash
# n8n 비밀번호 재설정
docker exec -it ai-n8n n8n user-management:reset --email=admin

# Grafana 비밀번호 재설정
docker exec -it ai-grafana grafana-cli admin reset-admin-password newpassword
```

## 📚 참고 자료

- [n8n 환경 변수 문서](https://docs.n8n.io/hosting/environment-variables/)
- [Grafana 설정 문서](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/)
- [Docker Compose 환경 변수](https://docs.docker.com/compose/environment-variables/)

---

**💡 TIP:** 개발 환경에서는 `.env.example`을 그대로 사용해도 되지만, 프로덕션에서는 반드시 강력한 비밀번호로 변경하세요!

