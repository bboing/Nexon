# 🛠️ 관리 스크립트 가이드

이 디렉토리에는 AI 플랫폼을 쉽게 관리할 수 있는 스크립트들이 포함되어 있습니다.

## 📋 스크립트 목록

### 🚀 기본 관리

| 스크립트 | 설명 | 사용법 |
|---------|------|--------|
| `start-all.sh` | 전체 서비스 시작 | `./scripts/start-all.sh` |
| `stop-all.sh` | 전체 서비스 중지 | `./scripts/stop-all.sh` |
| `restart-all.sh` | 전체 서비스 재시작 | `./scripts/restart-all.sh` |
| `status.sh` | 서비스 상태 확인 | `./scripts/status.sh` |

### 📊 단계별 시작 (READMEPJ.md 기반)

| 스크립트 | Phase | 포함 서비스 |
|---------|-------|-----------|
| `start-core.sh` | Day 1 | Ollama + Nginx |
| `start-workflow.sh` | Day 2 | n8n |
| `start-monitoring.sh` | Day 5 | Prometheus + Loki + Grafana |

### 🔧 유틸리티

| 스크립트 | 설명 | 사용법 |
|---------|------|--------|
| `logs.sh` | 로그 확인 | `./scripts/logs.sh [서비스명]` |
| `ollama-pull.sh` | 모델 다운로드 | `./scripts/ollama-pull.sh llama2` |
| `backup.sh` | 데이터 백업 | `./scripts/backup.sh` |
| `update.sh` | 이미지 업데이트 | `./scripts/update.sh` |
| `cleanup.sh` | 전체 정리 (⚠️ 주의) | `./scripts/cleanup.sh` |

## 🎯 일반적인 사용 시나리오

### 1️⃣ 처음 시작하기

```bash
# 권한 부여
chmod +x scripts/*.sh

# 전체 시작
./scripts/start-all.sh

# 상태 확인
./scripts/status.sh
```

### 2️⃣ 단계별로 시작하기 (권장)

```bash
# Phase 1: 코어 서비스
./scripts/start-core.sh

# Ollama 모델 다운로드
./scripts/ollama-pull.sh llama2

# Phase 2: 워크플로우
./scripts/start-workflow.sh

# Phase 5: 모니터링
./scripts/start-monitoring.sh
```

### 3️⃣ 로그 확인

```bash
# 전체 로그
./scripts/logs.sh

# 특정 서비스
./scripts/logs.sh ollama
./scripts/logs.sh n8n
./scripts/logs.sh grafana
```

### 4️⃣ 백업 및 복원

```bash
# 백업
./scripts/backup.sh

# 복원 (수동)
tar -xzf backups/ai-platform-backup-20240106_120000.tar.gz
```

### 5️⃣ 업데이트

```bash
# 이미지 업데이트
./scripts/update.sh

# 상태 확인
./scripts/status.sh
```

### 6️⃣ 문제 해결

```bash
# 재시작
./scripts/restart-all.sh

# 로그 확인
./scripts/logs.sh

# 완전 재설치 (데이터 삭제 주의!)
./scripts/cleanup.sh
./scripts/start-all.sh
```

## 💡 팁

### 권한 오류 발생 시

```bash
chmod +x scripts/*.sh
```

### 스크립트를 PATH에 추가

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export PATH="$PATH:/Users/taegyunkim/bboing/ollama_model/my-ai-platform/scripts"

# 그러면 어디서든 실행 가능
start-all.sh
status.sh
```

### 별칭(Alias) 설정

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
alias ai-start="cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform && ./scripts/start-all.sh"
alias ai-stop="cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform && ./scripts/stop-all.sh"
alias ai-status="cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform && ./scripts/status.sh"
alias ai-logs="cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform && ./scripts/logs.sh"
```

## 🔒 보안 주의사항

- `cleanup.sh`는 모든 데이터를 삭제하므로 주의하세요
- 백업은 정기적으로 수행하세요
- `.env` 파일은 절대 공유하지 마세요

## 🤝 추가 스크립트 제안

더 필요한 스크립트가 있다면 이슈를 등록해주세요!

