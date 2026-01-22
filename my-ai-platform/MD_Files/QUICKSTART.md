# ⚡ 빠른 시작 가이드

## 🎯 3분 안에 시작하기

### 1️⃣ .env 파일 생성 (30초)

```bash
cd my-ai-platform

# 최소 설정 복사
cp env.minimal .env

# 비밀번호 수정
nano .env
```

**수정할 부분:**
```env
N8N_PASSWORD=YourStrongPassword123!
GRAFANA_PASSWORD=YourStrongPassword456!
```

저장: `Ctrl+X` → `Y` → `Enter`

### 2️⃣ 시작하기 (1분)

```bash
./scripts/start-all.sh
```

기다리면 자동으로 모든 서비스 시작! ☕

### 3️⃣ 접속하기 (30초)

브라우저에서 열기:

- **n8n**: http://localhost:5678
- **Grafana**: http://localhost:3000
- **Ollama**: http://localhost:11434

로그인:
- ID: `admin`
- 비밀번호: `.env`에서 설정한 것

### 4️⃣ Ollama 모델 다운로드 (1분)

```bash
./scripts/ollama-pull.sh llama2
```

### 5️⃣ 테스트 (30초)

```bash
docker exec -it ai-ollama ollama run llama2 "안녕하세요"
```

## 🍎 Mac 사용자

**아무 추가 설정 없이 바로 시작하세요!**

```bash
cp env.minimal .env
nano .env  # 비밀번호만 수정
./scripts/start-all.sh
```

Apple Silicon (M1/M2/M3)은 자동으로 GPU 가속됩니다! 🚀

## 🐧 Linux + NVIDIA GPU

**GPU 가속 활성화:**

```bash
# 1. NVIDIA Container Toolkit 설치 (처음 1번만)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 2. GPU 설정 활성화
cp docker-compose.gpu.yml docker-compose.override.yml

# 3. 시작
./scripts/start-all.sh
```

## 📝 전체 명령어 요약

```bash
# 설정
cd my-ai-platform
cp env.minimal .env
nano .env

# Mac: 바로 시작
./scripts/start-all.sh

# Linux NVIDIA: GPU 활성화 후 시작
cp docker-compose.gpu.yml docker-compose.override.yml
./scripts/start-all.sh

# 모델 다운로드
./scripts/ollama-pull.sh llama2

# 테스트
docker exec -it ai-ollama ollama run llama2 "Hello"

# 상태 확인
./scripts/status.sh

# 로그 확인
./scripts/logs.sh
```

## 🎓 다음 단계

- 📖 **전체 가이드**: `README.md`
- 🖥️ **플랫폼별 설정**: `PLATFORM_GUIDE.md`
- 🎮 **GPU 설정**: `GPU_SETUP.md`
- 🔧 **환경 변수**: `ENV_GUIDE.md`

## 🆘 문제 발생 시

```bash
# 재시작
./scripts/restart-all.sh

# 로그 확인
./scripts/logs.sh

# 상태 확인
./scripts/status.sh

# 완전 재설치
./scripts/cleanup.sh
./scripts/start-all.sh
```

---

**🎉 완료! 이제 AI 플랫폼을 사용할 수 있습니다!**
