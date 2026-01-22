# 🎮 MLX 학습 모델 테스트 가이드

MLX로 학습한 모델을 테스트하는 3가지 방법을 안내합니다.

---

## 방법 1: 빠른 테스트 (Python 스크립트) ⚡ 추천!

가장 간단하고 빠른 방법입니다. MLX 환경에서 바로 테스트할 수 있습니다.

### 1️⃣ 기본 테스트 (5개 예시)

```bash
cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform/training

# MLX 환경 활성화
source mlx-env/bin/activate

# 테스트 실행
python scripts/test_mlx_model.py
```

**출력 예시**:
```
🎮 테스트 1/5
📝 프롬프트:
플레이어: 이 마을에 무슨 일이 있었나요?
NPC:

🤖 AI 응답:
*깊은 한숨을 쉬며* 최근 몬스터들이 마을 근처에 자주 출몰하고 있습니다...
```

---

### 2️⃣ 대화형 모드 (Interactive)

실제 대화하듯이 테스트할 수 있습니다.

```bash
python scripts/test_mlx_model.py --interactive
```

**대화 예시**:
```
👤 플레이어: 안녕하세요!
🤖 NPC: 환영합니다, 여행자여!

👤 플레이어: 검을 사고 싶어요
🤖 NPC: *철퇴로 쇠를 두드리며* 좋은 검을 원하신다면 500골드입니다!

👤 플레이어: exit
👋 대화를 종료합니다.
```

---

### 3️⃣ 커스텀 프롬프트 테스트

직접 프롬프트를 입력하여 테스트:

```bash
python scripts/test_mlx_model.py "플레이어: 마법을 배우고 싶어요\nNPC:"
```

---

## 방법 2: Jupyter Notebook 🔬

시각적으로 테스트하고 싶다면:

```bash
cd training
source mlx-env/bin/activate
pip install jupyter

# Jupyter 시작
jupyter notebook
```

**새 노트북에서**:
```python
from mlx_lm import load, generate

# 모델 로드
model, tokenizer = load(
    "mlx-community/Llama-3.2-3B-Instruct-4bit",
    adapter_path="models/llama-game-npc-mlx"
)

# 테스트
prompt = "플레이어: 안녕하세요!\nNPC:"
response = generate(model, tokenizer, prompt=prompt, max_tokens=100)
print(response)
```

---

## 방법 3: Ollama + WebUI 연동 🌐

MLX 모델을 GGUF로 변환하여 Ollama에 업로드하면 WebUI에서 사용 가능합니다.

### ⚠️ 주의사항

- **복잡도**: 높음 (여러 단계 필요)
- **시간**: 30분~1시간
- **필요 도구**: llama.cpp

### 단계별 가이드

#### 1️⃣ llama.cpp 설치

```bash
cd ~
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make
```

#### 2️⃣ MLX → GGUF 변환

```bash
cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform/training
source mlx-env/bin/activate

# 변환 스크립트 실행
python scripts/convert_to_gguf.py
```

**변환 과정**:
1. MLX LoRA 어댑터 + 기본 모델 병합
2. 병합된 모델을 GGUF 형식으로 변환
3. Ollama Modelfile 자동 생성

#### 3️⃣ Ollama에 등록

```bash
cd /Users/taegyunkim/bboing/ollama_model/my-ai-platform/training/models

# Ollama 모델 생성
ollama create game-npc -f Modelfile
```

#### 4️⃣ WebUI에서 사용

1. WebUI 접속: http://localhost:8090
2. 모델 선택 드롭다운에서 `game-npc` 선택
3. 대화 시작!

---

## 📊 방법 비교

| 방법 | 난이도 | 속도 | 장점 | 단점 |
|------|--------|------|------|------|
| **Python 스크립트** ⭐ | 쉬움 | 빠름 | 즉시 테스트 가능 | CLI만 |
| **Jupyter Notebook** | 중간 | 빠름 | 시각적, 대화형 | 설정 필요 |
| **Ollama + WebUI** | 어려움 | 느림 | 웹 인터페이스 | 변환 과정 복잡 |

---

## 🎯 추천 워크플로우

```
1️⃣ 빠른 검증
   → Python 스크립트로 기본 테스트
   → 응답 품질 확인

2️⃣ 추가 학습 필요?
   YES → 데이터 추가 & 재학습
   NO  → 3단계로

3️⃣ 배포 준비
   → GGUF 변환
   → Ollama 등록
   → WebUI 통합
```

---

## 🐛 트러블슈팅

### 문제: `mlx_lm` 모듈을 찾을 수 없음

```bash
# MLX 환경 활성화 확인
source mlx-env/bin/activate

# 패키지 재설치
pip install mlx mlx-lm
```

### 문제: 모델 응답이 이상함

**원인**: 학습이 부족하거나 데이터 품질 문제

**해결**:
1. Loss 확인: `training/models/llama-game-npc-mlx/adapter_config.json`
2. 더 많은 iters로 재학습: `CONFIG["iters"] = 500`
3. 데이터 품질 확인: `training/data/train.jsonl`

### 문제: GGUF 변환 실패

**원인**: llama.cpp 미설치 또는 버전 문제

**해결**:
```bash
cd ~/llama.cpp
git pull  # 최신 버전으로 업데이트
make clean
make
```

---

## 💡 팁

### 응답 품질 조정

```python
response = generate(
    model, tokenizer, prompt=prompt,
    max_tokens=100,      # 길이 조절
    temp=0.7,            # 창의성 (0.0~1.0, 높을수록 창의적)
    top_p=0.9,           # 다양성
    repetition_penalty=1.1,  # 반복 방지
)
```

### 여러 응답 비교

```python
for i in range(3):
    response = generate(model, tokenizer, prompt=prompt, temp=0.8)
    print(f"응답 {i+1}: {response}\n")
```

---

## 📚 다음 단계

- ✅ 기본 테스트 완료
- ✅ 응답 품질 확인
- [ ] 더 많은 데이터로 재학습
- [ ] Ollama 통합
- [ ] 프로덕션 배포

---

**문제가 있나요?** `MLX_FINETUNING_COMPLETE_GUIDE.md`의 트러블슈팅 섹션을 참고하세요!
