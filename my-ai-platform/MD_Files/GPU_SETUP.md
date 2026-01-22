# 🎮 GPU 설정 가이드

## 🍎 Mac 사용자

### Apple Silicon (M1/M2/M3/M4)

**✅ 좋은 소식: 추가 설정 불필요!**

- Ollama가 자동으로 **Metal**을 통해 GPU 가속
- `docker-compose.yml` 그대로 사용하면 됨
- NVIDIA 설정은 무시됨

```bash
# 그냥 시작하면 됩니다
./scripts/start-all.sh
```

**성능 확인:**
```bash
# 모델 실행 속도 체크
docker exec -it ai-ollama ollama run llama2 "Hello"
# 빠르면 GPU 가속 중!
```

### Intel Mac

- CPU 모드로 실행됨
- GPU 가속 없음 (정상)
- 작은 모델 사용 권장 (llama2:7b, gemma:2b)

---

## 🐧 Linux + NVIDIA GPU 사용자

### 1️⃣ 사전 요구사항

```bash
# NVIDIA 드라이버 확인
nvidia-smi

# NVIDIA Container Toolkit 설치
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Docker 재시작
sudo systemctl restart docker
```

### 2️⃣ GPU 활성화 방법

**방법 A: Override 파일 사용 (권장)**

```bash
cd my-ai-platform

# override 파일로 변경
cp docker-compose.gpu.yml docker-compose.override.yml

# 평소처럼 시작 (자동으로 GPU 설정 적용)
docker-compose up -d
# 또는
./scripts/start-all.sh
```

**방법 B: 직접 지정**

```bash
# 명시적으로 GPU 설정 파일 사용
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**방법 C: docker-compose.yml 직접 수정**

```yaml
# docker-compose.yml에서 주석 해제
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

### 3️⃣ GPU 작동 확인

```bash
# GPU 사용 확인
docker exec -it ai-ollama nvidia-smi

# 또는 Ollama에서 확인
docker logs ai-ollama | grep -i gpu
```

---

## 🪟 Windows + WSL2 + NVIDIA GPU

### 1️⃣ WSL2에서 NVIDIA 설정

```powershell
# Windows에서 NVIDIA 드라이버 설치 (WSL2용)
# https://developer.nvidia.com/cuda/wsl 에서 다운로드

# WSL2 내부에서
wsl -d Ubuntu
```

### 2️⃣ Linux 가이드와 동일

위의 "Linux + NVIDIA GPU" 가이드를 따라하세요.

---

## 📊 성능 비교

| 환경 | 모델 로딩 | 응답 속도 | 권장 모델 크기 |
|------|----------|----------|---------------|
| **Mac M1/M2/M3** | 빠름 ⚡ | 빠름 ⚡ | 13B 이하 |
| **Linux NVIDIA** | 매우 빠름 🚀 | 매우 빠름 🚀 | 70B 가능 |
| **CPU만** | 느림 🐌 | 느림 🐌 | 7B 이하 권장 |

---

## 🧪 테스트 스크립트

### GPU 성능 테스트

```bash
#!/bin/bash
# gpu-test.sh

echo "🧪 GPU 성능 테스트"
echo ""

# 모델 다운로드
docker exec -it ai-ollama ollama pull llama2

# 응답 시간 측정
echo "테스트 1: 짧은 응답"
time docker exec ai-ollama ollama run llama2 "Hi" --verbose

echo ""
echo "테스트 2: 긴 응답"
time docker exec ai-ollama ollama run llama2 "Explain quantum physics"

echo ""
echo "✅ GPU 가속이 정상이면 위 명령이 빠르게 실행됩니다"
```

---

## 🔧 문제 해결

### Mac에서 "nvidia driver not found" 에러

```bash
# 정상입니다! GPU 설정이 주석 처리되었는지 확인
cat docker-compose.yml | grep -A 5 "# deploy:"

# 또는 컨테이너 재생성
docker-compose down
docker-compose up -d
```

### Linux에서 GPU 인식 안 됨

```bash
# 1. NVIDIA 드라이버 확인
nvidia-smi

# 2. Docker가 GPU를 볼 수 있는지 확인
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# 3. Container Toolkit 재설치
sudo apt-get install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

### 메모리 부족

```bash
# 작은 모델 사용
docker exec -it ai-ollama ollama pull gemma:2b
docker exec -it ai-ollama ollama pull llama2:7b

# 큰 모델 삭제
docker exec -it ai-ollama ollama rm llama2:70b
```

---

## 💡 권장 설정

### 🍎 Mac 사용자
```bash
# 기본 설정 그대로 사용
./scripts/start-all.sh

# 추천 모델
./scripts/ollama-pull.sh llama2        # 7B
./scripts/ollama-pull.sh mistral       # 7B
./scripts/ollama-pull.sh codellama     # 7B
```

### 🐧 Linux NVIDIA 사용자
```bash
# GPU 활성화
cp docker-compose.gpu.yml docker-compose.override.yml
./scripts/start-all.sh

# 큰 모델도 가능
./scripts/ollama-pull.sh llama2:13b
./scripts/ollama-pull.sh llama2:70b    # VRAM 40GB+ 필요
```

### 🖥️ CPU만 있는 경우
```bash
# 경량 모델만 사용
./scripts/ollama-pull.sh gemma:2b
./scripts/ollama-pull.sh phi
```

---

## 📚 참고 자료

- [Ollama Docker 가이드](https://github.com/ollama/ollama/blob/main/docs/docker.md)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [Apple Metal 성능](https://ollama.com/blog/metal-support)

---

**💡 TIP:** Mac이라면 별도 설정 없이 바로 시작하세요! Apple Silicon이 알아서 GPU 가속을 해줍니다. 🚀

