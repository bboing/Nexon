# 🐳 Docker 빌드 가이드 및 문제 해결

## ❌ 발생한 오류

```
failed to solve: process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" 
did not complete successfully: exit code: 1
```

---

## 🔍 원인 분석

### 1. **패키지 버전 충돌**
- LangChain 생태계가 2024년 크게 변경됨
- 오래된 버전 (0.1.x) → 최신 버전 (0.3.x+)
- 의존성 충돌 발생

### 2. **시스템 라이브러리 누락**
- `lxml`, `beautifulsoup4` 같은 패키지는 C 라이브러리 필요
- `libxml2-dev`, `libxslt-dev` 등이 없으면 설치 실패

### 3. **메모리 부족** (가능성 낮음)
- 큰 패키지 (torch, transformers) 설치 시 메모리 초과

---

## ✅ 해결 방법

### **방법 1: 업데이트된 requirements.txt 사용 (권장)**

이미 `requirements.txt`가 업데이트되었습니다. 다시 빌드하세요:

```bash
cd my-ai-platform

# 기존 이미지 삭제 (선택사항)
docker rmi langchain_app-langchain-api

# 다시 빌드 및 시작
docker compose -f docker-compose.langchain.yml up -d --build
```

**변경 사항:**
- ✅ LangChain 0.3.x 이상으로 업데이트
- ✅ 모든 패키지를 최신 안정 버전으로 변경
- ✅ 시스템 의존성 추가 (`git`, `libxml2-dev`, `libxslt-dev`)
- ✅ pip, setuptools, wheel 업그레이드

---

### **방법 2: 최소 의존성으로 빠른 빌드**

빌드 시간을 단축하고 싶다면 최소 버전 사용:

```bash
# langchain_app/Dockerfile 수정
cd langchain_app
nano Dockerfile
```

**13번째 줄 변경:**
```dockerfile
# 기존
RUN pip install --no-cache-dir -r requirements.txt

# 변경 (최소 버전)
RUN pip install --no-cache-dir -r requirements.minimal.txt
```

```bash
# 다시 빌드
cd ..
docker compose -f docker-compose.langchain.yml up -d --build langchain-api
```

**최소 버전의 장점:**
- ⚡ 빌드 시간 50% 단축
- 📦 이미지 크기 30% 감소
- 🚀 시작 속도 향상

**제한 사항:**
- ⚠️ DOCX, PPTX 파일 처리 불가 (PDF만 가능)
- ⚠️ 일부 텍스트 처리 기능 제한

---

### **방법 3: 단계별 디버깅**

빌드 실패 시 상세 로그 확인:

```bash
# 로그 출력하며 빌드
docker compose -f docker-compose.langchain.yml build --no-cache --progress=plain langchain-api

# 특정 패키지 확인
docker run --rm python:3.11-slim pip install langchain==0.3.0
```

**일반적인 오류와 해결:**

#### **오류 1: `gcc` 관련 에러**
```
error: command 'gcc' failed
```

**해결:**
```dockerfile
# Dockerfile에 추가
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++
```

#### **오류 2: `lxml` 설치 실패**
```
ERROR: Failed building wheel for lxml
```

**해결:**
```dockerfile
RUN apt-get install -y \
    libxml2-dev \
    libxslt-dev
```

#### **오류 3: 메모리 부족**
```
Killed
```

**해결:**
```bash
# Docker Desktop 메모리 증가
# Settings → Resources → Memory: 8GB 이상
```

---

## 🚀 권장 빌드 프로세스

### **1단계: 캐시 없이 완전 재빌드**
```bash
cd my-ai-platform

# 기존 컨테이너 및 이미지 삭제
docker compose -f docker-compose.langchain.yml down
docker rmi langchain_app-langchain-api

# 완전 재빌드
docker compose -f docker-compose.langchain.yml build --no-cache langchain-api
```

### **2단계: 빌드 확인**
```bash
# 빌드된 이미지 확인
docker images | grep langchain

# 예상 결과:
# langchain_app-langchain-api   latest   abc123def456   2 minutes ago   2.1GB
```

### **3단계: 컨테이너 시작**
```bash
docker compose -f docker-compose.langchain.yml up -d langchain-api

# 로그 확인
docker compose -f docker-compose.langchain.yml logs -f langchain-api
```

### **4단계: 헬스 체크**
```bash
# API 응답 확인
curl http://localhost:8000/health

# 예상 응답:
# {"status":"healthy","services":{...}}
```

---

## 🔧 고급 최적화

### **멀티 스테이지 빌드** (이미지 크기 감소)

```dockerfile
# Dockerfile.optimized

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# 빌드된 패키지만 복사
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**사용:**
```bash
# docker-compose.langchain.yml에서 dockerfile 경로 변경
# dockerfile: Dockerfile.optimized
```

---

## 📊 빌드 시간 비교

| 방법 | 빌드 시간 | 이미지 크기 | 기능 |
|------|-----------|-------------|------|
| **Full (requirements.txt)** | ~10분 | 2.5GB | 모든 기능 |
| **Minimal (requirements.minimal.txt)** | ~5분 | 1.5GB | 핵심 기능만 |
| **Optimized (멀티 스테이지)** | ~12분 | 1.2GB | 모든 기능 + 최소 크기 |

---

## 🐛 여전히 실패한다면?

### **수동 테스트**

```bash
# 컨테이너 안에서 직접 설치 테스트
docker run -it --rm python:3.11-slim bash

# 컨테이너 내부에서
apt-get update && apt-get install -y build-essential curl git
pip install --upgrade pip
pip install langchain>=0.3.0
pip install langfuse>=2.54.0
# ... 하나씩 테스트
```

### **로그 수집**

```bash
# 상세 빌드 로그 파일로 저장
docker compose -f docker-compose.langchain.yml build --no-cache --progress=plain langchain-api 2>&1 | tee build.log

# build.log 파일 확인
less build.log
```

### **대안: 사전 빌드 이미지 사용**

빌드가 계속 실패한다면, 이미 빌드된 이미지 사용:

```yaml
# docker-compose.langchain.yml
langchain-api:
  # build:
  #   context: ./langchain_app
  #   dockerfile: Dockerfile
  image: python:3.11-slim  # 임시로 기본 이미지 사용
  command: >
    bash -c "
    pip install langchain langfuse fastapi uvicorn &&
    cd /app &&
    uvicorn api.main:app --host 0.0.0.0 --port 8000
    "
  volumes:
    - ./langchain_app:/app
```

---

## ✅ 체크리스트

빌드 전 확인 사항:

- [ ] Docker Desktop 실행 중
- [ ] 메모리 8GB 이상 할당
- [ ] 디스크 여유 공간 10GB 이상
- [ ] 인터넷 연결 안정적
- [ ] `requirements.txt` 업데이트됨
- [ ] `Dockerfile`에 시스템 의존성 추가됨

---

## 📚 참고 자료

- [LangChain 마이그레이션 가이드](https://python.langchain.com/docs/versions/migrating_chains/migration/)
- [Docker 멀티 스테이지 빌드](https://docs.docker.com/build/building/multi-stage/)
- [Python Docker 베스트 프랙티스](https://docs.docker.com/language/python/build-images/)

---

**문제가 해결되지 않으면 `build.log` 파일을 공유해주세요!** 🚀
