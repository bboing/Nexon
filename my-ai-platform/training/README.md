# 🍎 Apple MLX Training Environment

Apple Silicon (M1/M2/M3) Mac에 최적화된 LLM 파인튜닝 환경입니다.

## 📁 디렉토리 구조

```
training/
├── mlx-env/        # MLX Python 가상환경
├── data/           # 학습 데이터셋 (JSONL)
├── scripts/        # 파인튜닝 스크립트 (finetune_mlx.py)
├── models/         # 학습된 모델 저장
├── output/         # 학습 로그, 체크포인트
└── MLX_GUIDE.md    # 상세 가이드
```

## 🚀 빠른 시작

### 1. MLX 파인튜닝 실행

```bash
# 프로젝트 루트에서
sh scripts/start-mlx-training.sh
```

**자동으로 진행**:
- ✅ MLX 환경 설정
- ✅ 샘플 데이터 생성
- ✅ 모델 다운로드
- ✅ LoRA 파인튜닝
- ✅ 추론 테스트

### 2. 커스텀 데이터로 학습

```bash
# 데이터 준비
vi data/train.jsonl

# 학습 실행
sh ../scripts/start-mlx-training.sh
```

## 📝 데이터셋 형식

### JSONL 형식 (MLX)

```jsonl
{"text": "당신은 게임 NPC입니다. 플레이어: 안녕하세요. NPC: 환영합니다!"}
{"text": "당신은 상인입니다. 플레이어: 검을 팔나요? NPC: 네, 있습니다."}
```

### 예시 (게임 NPC)

```jsonl
{"text": "당신은 판타지 게임의 대장장이 NPC입니다. 플레이어: 좋은 검을 추천해주세요. NPC: *철퇴로 쇠를 두드리며* 흠... 미스릴 장검이 어울리겠습니다."}
{"text": "당신은 엘프 마을의 장로입니다. 플레이어: 숲의 북쪽 길을 알려주세요. NPC: 위험하지만 고대 유적이 있습니다."}
```

## 🍎 MLX 장점

- **Metal 가속**: M1/M2/M3 GPU 활용
- **빠른 속도**: PyTorch CPU 대비 5~10배
- **메모리 효율**: Unified Memory 사용
- **간단한 설치**: pip만으로 완료

## 📊 학습 후 프로세스

1. **모델 테스트**: Python에서 직접 추론
2. **추가 학습**: 더 많은 데이터로 재학습
3. **Ollama 통합**: 프로덕션 배포 (선택)
4. **성능 평가**: Langfuse로 추적

## ⚙️ 설정 변경

`scripts/finetune_mlx.py`:

```python
CONFIG = {
    "model": "mlx-community/Llama-3.2-1B-Instruct-4bit",
    "iters": 1000,  # 학습 반복 횟수
    "lora_rank": 16,  # LoRA rank (8~32)
    "batch_size": 4,  # 배치 크기
}
```

## 🔗 관련 문서

- [MLX 공식 문서](https://github.com/ml-explore/mlx)
- [mlx-lm GitHub](https://github.com/ml-explore/mlx-examples/tree/main/llms)
- [MLX_GUIDE.md](MLX_GUIDE.md) - 상세 가이드
