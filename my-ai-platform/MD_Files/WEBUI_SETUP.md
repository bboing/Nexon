# 🎨 Open WebUI 설정 가이드

## 📖 Open WebUI란?

Ollama를 위한 ChatGPT 스타일의 웹 인터페이스입니다.

**주요 기능:**
- 💬 웹 브라우저에서 AI 채팅
- 🔄 여러 모델 간 쉬운 전환
- 💾 대화 히스토리 저장
- 📎 파일 업로드 (PDF, 이미지)
- 🎨 커스텀 프롬프트
- 👥 다중 사용자 지원
- 🔍 RAG (문서 검색) 기능

## 🚀 빠른 설치

### 방법 1: Override 파일 사용 (권장)

```bash
cd my-ai-platform

# 1. WebUI 활성화
cp docker-compose.webui.yml docker-compose.override.yml

# 2. .env에 설정 추가
cat >> .env << 'EOF'

# Open WebUI 설정
OPENWEBUI_VERSION=latest
OPENWEBUI_PORT=8080
WEBUI_AUTH=true
WEBUI_SECRET_KEY=MySecretKey123!
EOF

# 3. 시작
docker-compose up -d
```

### 방법 2: 직접 실행

```bash
docker-compose -f docker-compose.yml -f docker-compose.webui.yml up -d
```

### 방법 3: 독립 실행 (가장 빠름)

```bash
docker run -d \
  --name ai-open-webui \
  -p 8080:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui-data:/app/backend/data \
  ghcr.io/open-webui/open-webui:latest
```

## 🎯 설치 후 접속

### 1️⃣ 브라우저에서 열기

```
http://localhost:8080
```

### 2️⃣ 첫 계정 생성

- 첫 번째 등록자가 **관리자**가 됩니다
- 이메일과 비밀번호 설정
- 로그인

### 3️⃣ 모델 선택

- 좌측 상단에서 모델 선택
- 먼저 Ollama에서 모델 다운로드 필요:

```bash
./scripts/ollama-pull.sh llama2
./scripts/ollama-pull.sh mistral
./scripts/ollama-pull.sh codellama
```

### 4️⃣ 채팅 시작! 🎉

## 📊 서비스 구성도

```
사용자 → Open WebUI (8080) → Ollama (11434) → LLM 모델
                ↓
              Nginx (80)
                ↓
          n8n (5678) ← Webhook
                ↓
           Grafana (3000)
```

## 🔧 환경 변수

```bash
# .env에 추가
OPENWEBUI_VERSION=latest          # 버전 (latest, v0.3.0 등)
OPENWEBUI_PORT=8080               # 웹 포트
WEBUI_AUTH=true                   # 인증 활성화
WEBUI_SECRET_KEY=YourSecretKey    # 세션 암호화 키
```

## 🎨 주요 기능 사용법

### 1️⃣ 모델 전환

- 채팅 화면 상단의 드롭다운
- 실시간으로 모델 변경 가능
- 각 대화마다 다른 모델 사용 가능

### 2️⃣ 파일 업로드 (RAG)

```bash
1. 채팅창의 📎 아이콘 클릭
2. PDF, TXT, 이미지 업로드
3. "이 문서에 대해 설명해줘" 질문
4. AI가 문서 내용 기반 답변
```

### 3️⃣ 커스텀 프롬프트

```
Settings → Prompts → Create Prompt

예시:
Name: 한국어 번역기
Prompt: |
  당신은 전문 번역가입니다.
  다음 텍스트를 한국어로 정확하게 번역하세요:
  {{input}}
```

### 4️⃣ 대화 저장 & 공유

- 각 대화는 자동 저장
- 좌측 사이드바에서 대화 기록 확인
- 공유 링크 생성 가능

## 🔗 Nginx 통합

Open WebUI를 Nginx로 라우팅하려면:

### nginx/nginx.conf에 추가:

```nginx
# Open WebUI
server {
    listen 80;
    server_name chat.localhost;

    location / {
        proxy_pass http://open-webui:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 웹소켓 지원
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### /etc/hosts 추가:

```bash
sudo nano /etc/hosts

# 추가
127.0.0.1 chat.localhost
```

**접속:** http://chat.localhost

## 🛡️ 보안 설정

### 1️⃣ 인증 활성화 (기본값)

```env
WEBUI_AUTH=true
```

### 2️⃣ 회원가입 제한 (관리자 후)

Open WebUI 관리자 패널:
```
Settings → Admin → Disable New User Registration
```

### 3️⃣ HTTPS 설정 (프로덕션)

```bash
# Let's Encrypt 인증서
sudo certbot --nginx -d yourdomain.com
```

## 📈 성능 최적화

### 여러 모델 동시 사용

```env
# .env에 추가
OLLAMA_MAX_LOADED_MODELS=3
OLLAMA_NUM_PARALLEL=4
```

### 메모리 제한

```yaml
# docker-compose.webui.yml
open-webui:
  deploy:
    resources:
      limits:
        memory: 2G
```

## 🧪 테스트

### API 확인

```bash
# Open WebUI 상태
curl http://localhost:8080/health

# Ollama 연결 테스트
docker logs ai-open-webui | grep -i ollama
```

### 문제 해결

```bash
# 로그 확인
docker logs -f ai-open-webui

# 재시작
docker-compose restart open-webui

# 데이터 초기화
docker volume rm open-webui-data
docker-compose up -d
```

## 🆚 Open WebUI vs n8n

| 기능 | Open WebUI | n8n |
|------|-----------|-----|
| **용도** | 사람이 채팅 | 자동화 워크플로우 |
| **UI** | 채팅 인터페이스 | 노드 기반 |
| **대화 저장** | ✅ | ❌ |
| **파일 업로드** | ✅ PDF, 이미지 | ✅ 프로그래밍 방식 |
| **사용자 관리** | ✅ | ✅ |
| **RAG** | ✅ 내장 | ✅ 커스텀 |
| **자동화** | ❌ | ✅ |

**결론:** 둘 다 사용하세요!
- Open WebUI: 대화형 테스트, 사용자 채팅
- n8n: 자동화, 백엔드 통합

## 📦 전체 설치 스크립트

```bash
#!/bin/bash
# install-webui.sh

cd my-ai-platform

# 1. Override 파일 생성
cp docker-compose.webui.yml docker-compose.override.yml

# 2. .env 업데이트
if ! grep -q "OPENWEBUI" .env; then
    cat >> .env << 'EOF'

# Open WebUI 설정
OPENWEBUI_VERSION=latest
OPENWEBUI_PORT=8080
WEBUI_AUTH=true
WEBUI_SECRET_KEY=$(openssl rand -hex 32)
EOF
fi

# 3. 시작
docker-compose up -d open-webui

# 4. 대기
sleep 5

# 5. 상태 확인
docker logs ai-open-webui --tail=20

echo ""
echo "✅ Open WebUI가 시작되었습니다!"
echo "🌐 접속: http://localhost:8080"
echo "👤 첫 계정을 생성하세요 (관리자가 됩니다)"
```

## 🎓 추가 학습 자료

- [Open WebUI 공식 문서](https://docs.openwebui.com/)
- [Open WebUI GitHub](https://github.com/open-webui/open-webui)
- [Ollama 모델 라이브러리](https://ollama.ai/library)

---

**💡 TIP:** Open WebUI를 추가하면 Ollama를 훨씬 쉽게 사용할 수 있어요! 브라우저에서 바로 ChatGPT처럼 사용 가능합니다! 🚀

