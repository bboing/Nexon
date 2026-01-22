# 🖥️ 플랫폼별 설정 가이드

## 빠른 비교표

| 플랫폼 | GPU 지원 | 추가 설정 | 권장 모델 크기 |
|--------|---------|----------|---------------|
| **Mac M1/M2/M3** | ✅ Metal (자동) | 불필요 | ~13B |
| **Mac Intel** | ❌ CPU만 | 불필요 | ~7B |
| **Linux NVIDIA** | ✅ CUDA | 필요 | ~70B |
| **Linux AMD** | ⚠️ ROCm | 복잡 | ~13B |
| **Windows WSL2** | ✅ CUDA | 필요 | ~70B |
| **Windows Native** | ❌ 비추천 | - | - |

---

## 🍎 Mac (macOS)

### ✅ 설정 완료! 바로 시작하세요

```bash
cd my-ai-platform

# 1. .env 파일 생성
cp env.minimal .env
nano .env  # 비밀번호 수정

# 2. 시작
./scripts/start-all.sh

# 3. 모델 다운로드
./scripts/ollama-pull.sh llama2
```

### 🎯 Mac 특징

**Apple Silicon (M1/M2/M3/M4):**
- ✅ Metal을 통한 자동 GPU 가속
- ✅ 통합 메모리 활용 (8GB~96GB)
- ✅ 전력 효율적
- 🚀 7B 모델은 매우 빠름
- ⚠️ 13B 이상은 메모리에 따라 다름

**Intel Mac:**
- ⚠️ CPU 모드만
- ⚠️ 7B 이하 모델 권장
- ⚠️ 느린 응답 속도

### 📝 Mac에서 주의사항

```bash
# ❌ 이런 에러가 나면
Error: nvidia driver not found

# ✅ 정상입니다! 무시하세요
# docker-compose.yml에서 GPU 설정이 주석 처리되어야 함
```

---

## 🐧 Linux

### NVIDIA GPU 있는 경우

**1️⃣ NVIDIA Container Toolkit 설치**

```bash
# Ubuntu/Debian
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**2️⃣ GPU 활성화**

```bash
cd my-ai-platform

# GPU 설정 활성화
cp docker-compose.gpu.yml docker-compose.override.yml

# .env 설정
cp env.minimal .env
nano .env

# 시작
./scripts/start-all.sh
```

**3️⃣ GPU 확인**

```bash
# GPU 작동 확인
docker exec -it ai-ollama nvidia-smi

# 모델 실행 테스트
./scripts/ollama-pull.sh llama2
docker exec -it ai-ollama ollama run llama2 "Hello"
```

### CPU만 있는 경우

```bash
# 기본 설정 사용
./scripts/start-all.sh

# 경량 모델 사용
./scripts/ollama-pull.sh gemma:2b
./scripts/ollama-pull.sh phi
```

---

## 🪟 Windows

### WSL2 사용 (권장) ✅

**1️⃣ WSL2 설치**

```powershell
# PowerShell (관리자 권한)
wsl --install -d Ubuntu
```

**2️⃣ NVIDIA GPU 지원 (GPU가 있는 경우)**

1. Windows에서 NVIDIA 드라이버 설치
   - [CUDA on WSL](https://developer.nvidia.com/cuda/wsl)에서 다운로드
   - WSL2용 특수 드라이버 필요

2. WSL2 내부에서 Linux 가이드 따라하기
   ```bash
   wsl -d Ubuntu
   cd /mnt/c/Users/YourName/my-ai-platform
   # Linux NVIDIA 가이드 참고
   ```

**3️⃣ Docker Desktop 사용**

- Docker Desktop for Windows 설치
- WSL2 integration 활성화
- Settings → Resources → WSL Integration

### Windows Native (비추천) ⚠️

- Docker Desktop의 Windows Container는 제한적
- WSL2 사용을 강력히 권장

---

## 🔧 플랫폼별 최적 설정

### Mac M1/M2/M3 최적화

```bash
# .env 설정
N8N_USER=admin
N8N_PASSWORD=YourPassword123!
GRAFANA_USER=admin
GRAFANA_PASSWORD=YourPassword456!

# 추천 모델 (메모리별)
# 8GB RAM
./scripts/ollama-pull.sh gemma:2b
./scripts/ollama-pull.sh phi

# 16GB RAM
./scripts/ollama-pull.sh llama2
./scripts/ollama-pull.sh mistral
./scripts/ollama-pull.sh codellama

# 32GB+ RAM
./scripts/ollama-pull.sh llama2:13b
./scripts/ollama-pull.sh mixtral
```

### Linux NVIDIA 최적화

```bash
# GPU 메모리별 권장 모델
# 8GB VRAM
./scripts/ollama-pull.sh llama2
./scripts/ollama-pull.sh mistral

# 16GB VRAM
./scripts/ollama-pull.sh llama2:13b
./scripts/ollama-pull.sh mixtral

# 24GB+ VRAM (3090, 4090, A100)
./scripts/ollama-pull.sh llama2:70b
./scripts/ollama-pull.sh mixtral:8x7b

# 메모리 부족 시 양자화 모델
./scripts/ollama-pull.sh llama2:7b-q4_0  # 4-bit
```

### CPU 전용 최적화

```bash
# 경량 모델만 사용
./scripts/ollama-pull.sh gemma:2b
./scripts/ollama-pull.sh phi:2.7b
./scripts/ollama-pull.sh tinyllama

# 쓰레드 수 제한 (env 파일에 추가)
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

---

## 🧪 성능 테스트

### 벤치마크 스크립트

```bash
#!/bin/bash
# benchmark.sh

echo "🧪 플랫폼 성능 테스트"
echo ""

# 시스템 정보
echo "📊 시스템 정보:"
uname -a

if [[ "$OSTYPE" == "darwin"* ]]; then
    sysctl -n machdep.cpu.brand_string
    sysctl hw.memsize
elif command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv
fi

echo ""
echo "⏱️ 응답 시간 측정..."

# 모델 다운로드
docker exec ai-ollama ollama pull llama2 2>/dev/null

# 테스트
echo "Test 1: 짧은 응답"
time docker exec ai-ollama ollama run llama2 "Hi" 2>/dev/null

echo ""
echo "Test 2: 중간 응답"
time docker exec ai-ollama ollama run llama2 "Explain AI in one paragraph" 2>/dev/null
```

```bash
chmod +x benchmark.sh
./benchmark.sh
```

---

## 📊 예상 성능

### 응답 속도 비교 (llama2:7b 기준)

| 플랫폼 | 초기 로딩 | 토큰/초 |
|--------|----------|---------|
| Mac M1 | ~2초 | ~20 |
| Mac M2 Pro | ~1초 | ~30 |
| Mac M3 Max | ~1초 | ~50 |
| RTX 3090 | ~1초 | ~60 |
| RTX 4090 | <1초 | ~100 |
| CPU (i9) | ~5초 | ~5 |

---

## 🆘 플랫폼별 문제 해결

### Mac 문제

```bash
# Docker가 느린 경우
# Docker Desktop → Settings → Resources
# CPU: 최소 4코어
# Memory: 최소 8GB
# Disk: 최소 20GB

# 재시작
./scripts/restart-all.sh
```

### Linux 문제

```bash
# GPU 인식 안 됨
sudo nvidia-smi  # 드라이버 확인
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi  # Docker GPU 테스트

# 권한 문제
sudo usermod -aG docker $USER
newgrp docker
```

### Windows WSL2 문제

```bash
# WSL2에서 Docker 안 보임
# Docker Desktop → Settings → Resources → WSL Integration
# Ubuntu 체크박스 활성화

# 재시작
wsl --shutdown
# Docker Desktop 재시작
```

---

## 💡 플랫폼별 권장 사항

### ✅ Mac 사용자께
- 그냥 시작하세요! 설정 필요 없음
- M1/M2/M3라면 13B 모델도 가능
- 메모리 16GB+ 권장

### ✅ Linux NVIDIA 사용자께
- GPU 설정 활성화 필수
- 큰 모델 사용 가능
- VRAM 확인 후 모델 선택

### ✅ CPU만 있는 사용자께
- 경량 모델 사용 (2B-7B)
- 인내심 필요 🐌
- 업그레이드 고려

---

**상세 GPU 설정:** `GPU_SETUP.md` 참고

