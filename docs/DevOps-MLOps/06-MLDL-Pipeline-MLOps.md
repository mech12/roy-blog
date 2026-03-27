# ML/DL 시스템 및 모델 개발 프로세스

> 다른 분야 시니어 엔지니어를 위한 핵심 용어 해설 포함

---

## 1. ML/DL 파이프라인 전체 흐름

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 데이터    │ → │ 전처리    │ → │ 모델 학습 │ → │ 평가/검증 │ → │ 배포     │
│ 수집      │   │ & 피처    │   │          │   │          │   │ & 서빙   │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                                                  ↓
                              ┌──────────┐                   ┌──────────┐
                              │ 재학습    │ ← ───────────── │ 모니터링 │
                              └──────────┘                   └──────────┘
```

---

## 2. 데이터 전처리 (Data Preprocessing)

### 핵심 용어

| 용어 | 설명 | 비유 |
|------|------|------|
| **Feature (피처)** | 모델 입력으로 사용하는 개별 변수/속성 | DB의 컬럼 |
| **Feature Engineering** | 원시 데이터에서 유의미한 피처를 설계/추출 | ETL에서 T (Transform) |
| **Normalization** | 값의 범위를 0~1로 조정 (Min-Max Scaling) | 단위 통일 |
| **Standardization** | 평균 0, 표준편차 1로 변환 (Z-score) | 표준화 |
| **One-Hot Encoding** | 범주형 변수를 이진 벡터로 변환 ("색상: 빨강" → [1,0,0]) | Enum → Bit Flag |
| **Tokenization** | 텍스트를 토큰(단어/서브워드) 단위로 분리 | 형태소 분석 |
| **Embedding** | 토큰/카테고리를 고차원 벡터로 변환 | 해시맵 (의미 보존) |
| **Data Augmentation** | 기존 데이터를 변형하여 학습 데이터 증강 (회전, 크롭 등) | 테스트 케이스 변형 |

### Feature Store

**한 줄 요약**: "ML 피처를 중앙에서 관리/공유하는 저장소"

```
원시 데이터 → Feature Pipeline → Feature Store → 학습/추론에서 재사용
                                  (Feast, Tecton)
```

- 피처 정의의 일관성 보장 (학습/추론 간 Skew 방지)
- 피처 재사용으로 팀 간 중복 작업 제거

---

## 3. 모델 학습 (Model Training)

### 핵심 용어

| 용어 | 설명 | 비유 |
|------|------|------|
| **Epoch** | 전체 학습 데이터를 1회 순회 | 교과서 1번 읽기 |
| **Batch** | 한 번에 처리하는 데이터 묶음 | 페이지 단위로 읽기 |
| **Batch Size** | 배치 내 샘플 수 (32, 64, 128 등) | 한번에 몇 페이지? |
| **Learning Rate** | 가중치 업데이트 크기 (너무 크면 발산, 작으면 느림) | 보폭 크기 |
| **Loss Function** | 예측값과 정답의 차이를 수치화 | 오차 측정 함수 |
| **Optimizer** | 손실을 줄이는 방향으로 가중치 업데이트하는 알고리즘 | 내비게이션 |
| **Gradient** | 손실 함수의 기울기 (어느 방향으로 얼마나 조정?) | 경사도 |
| **Backpropagation** | 출력→입력 방향으로 기울기를 전파하여 가중치 갱신 | 역추적 |
| **Overfitting** | 학습 데이터에 과적합 → 새 데이터에서 성능 저하 | 답을 외워버림 |
| **Underfitting** | 모델이 너무 단순하여 패턴을 못 잡음 | 공부 부족 |

### 학습 vs 추론

```
학습 (Training)                   추론 (Inference)
- GPU/TPU 대량 사용                - 상대적으로 적은 자원
- 시간 ~수시간~수일                 - 실시간 (수 ms~수 초)
- 모델 가중치 업데이트               - 가중치 고정, 예측만
- 배치 처리                        - 온라인/스트리밍 처리
```

---

## 4. 하이퍼파라미터 튜닝 (Hyperparameter Tuning)

### 하이퍼파라미터 vs 파라미터

| 구분 | 파라미터 (Parameter) | 하이퍼파라미터 (Hyperparameter) |
|------|---------------------|-------------------------------|
| **누가 정하나?** | 학습 과정에서 자동으로 학습 | 사람(또는 탐색 알고리즘)이 사전에 설정 |
| **예시** | 가중치, 바이어스 | Learning Rate, Batch Size, Layer 수 |
| **비유** | 시험 답안 | 공부 전략 (몇 시간 공부할지, 어떤 교재 쓸지) |

### 탐색 방법

| 방법 | 설명 | 장단점 |
|------|------|--------|
| **Grid Search** | 모든 조합을 격자형으로 시도 | 확실하지만 느림 (조합 폭발) |
| **Random Search** | 랜덤으로 조합 선택 | Grid보다 효율적, 운에 의존 |
| **Bayesian Optimization** | 이전 결과를 바탕으로 다음 탐색점 결정 | 효율적, 구현 복잡 |
| **Population-Based Training (PBT)** | 학습 중에 파라미터를 진화(evolution)시킴 | 동적 조정, 자원 많이 필요 |

```
Grid Search 예시:
  learning_rate: [0.001, 0.01, 0.1]
  batch_size: [32, 64, 128]
  → 3 × 3 = 9가지 조합 모두 시도

Bayesian Optimization:
  1차 시도: lr=0.01, bs=64 → 정확도 85%
  2차 시도: lr=0.005, bs=128 → 정확도 87% (더 나은 영역 탐색)
  3차 시도: lr=0.007, bs=96 → 정확도 89% (이전 결과 기반 추론)
```

---

## 5. 모델 최적화 (Optimization for Deployment)

### 경량화 기법

| 기법 | 설명 | 효과 |
|------|------|------|
| **Quantization (양자화)** | FP32 → INT8/FP16으로 정밀도 축소 | 모델 크기 2~4배 축소, 추론 속도 향상 |
| **Pruning (가지치기)** | 중요도 낮은 가중치/뉴런 제거 | 모델 경량화, 약간의 정확도 손실 |
| **Distillation (지식 증류)** | 큰 모델(Teacher)의 지식을 작은 모델(Student)에 전달 | 작은 모델로 유사 성능 |
| **ONNX 변환** | 프레임워크 독립적 형식으로 변환 | 다양한 런타임에서 실행 가능 |
| **TensorRT** | NVIDIA GPU 최적화 추론 엔진 | 레이어 퓨전, 커널 튜닝 → 수배 빠른 추론 |

### LoRA / QLoRA (LLM 파인튜닝)

**한 줄 요약**: "전체 모델 대신 소량의 추가 파라미터만 학습하는 효율적 파인튜닝"

```
기존 파인튜닝:                 LoRA:
  전체 가중치 업데이트           원래 가중치는 동결 (Frozen)
  (수십억 파라미터)              + 작은 행렬 A, B만 학습
  GPU 메모리 수백 GB 필요        (수백만 파라미터)
                               GPU 메모리 수십 GB로 가능

QLoRA:
  LoRA + 양자화 (4-bit)
  → 더 적은 메모리로 파인튜닝
```

---

## 6. 실험 추적 및 모델 관리

### MLflow

**한 줄 요약**: "ML 실험 추적, 모델 버전 관리, 배포를 위한 오픈소스 플랫폼"

```
┌─ MLflow 구성 요소 ──────────────────────────────────┐
│                                                      │
│  Tracking          Model Registry       Serving      │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐  │
│  │ 실험 기록   │    │ 모델 버전   │    │ REST API   │  │
│  │ - 파라미터  │ →  │ - v1, v2.. │ →  │ 모델 서빙   │  │
│  │ - 메트릭    │    │ - Staging  │    │ (Flask)    │  │
│  │ - 아티팩트  │    │ - Prod     │    │            │  │
│  └────────────┘    └────────────┘    └────────────┘  │
└──────────────────────────────────────────────────────┘
```

| 기능 | 설명 |
|------|------|
| **Experiment** | 관련 실험 묶음 (예: "BERT 분류기 실험") |
| **Run** | 1회 실험 실행 (파라미터, 메트릭, 모델 파일 기록) |
| **Model Registry** | 모델 버전 관리 + 스테이지 전환 (None → Staging → Production → Archived) |
| **Artifact** | 학습 결과물 (모델 파일, 그래프, 데이터셋) |
| **Auto-logging** | TensorFlow, PyTorch 등에서 자동으로 메트릭/파라미터 기록 |

### Weights & Biases (W&B)

- MLflow와 유사한 실험 추적 도구 (클라우드 기반 SaaS)
- 실시간 대시보드, 팀 협업, Sweep (자동 하이퍼파라미터 탐색)
- 연구팀에서 많이 사용 (시각화 UI가 우수)

### MLflow vs W&B 선택 기준

| 항목 | MLflow | W&B |
|------|--------|-----|
| **호스팅** | 자체 서버 (온프레미스 가능) | 클라우드 SaaS (자체 호스팅도 가능) |
| **비용** | 무료 오픈소스 | 무료 tier + 유료 |
| **모델 레지스트리** | 내장 (강력) | 제한적 |
| **시각화** | 기본 수준 | 매우 우수 |
| **벤더 종속** | 없음 | 있음 |

---

## 7. 모델 서빙 (Model Serving)

### 서빙 방식

| 방식 | 설명 | 용도 |
|------|------|------|
| **Batch Inference** | 주기적으로 대량 데이터를 한꺼번에 추론 | 추천 시스템 사전 계산 |
| **Online Inference** | REST/gRPC API로 실시간 추론 | 챗봇, 실시간 분류 |
| **Streaming Inference** | 데이터 스트림에서 연속 추론 | 이상 감지, 실시간 번역 |

### 서빙 프레임워크

| 도구 | 설명 |
|------|------|
| **TorchServe** | PyTorch 모델 서빙 (REST/gRPC) |
| **TF Serving** | TensorFlow 모델 서빙 |
| **Triton Inference Server** | NVIDIA, 멀티프레임워크 + GPU 최적화 |
| **vLLM** | LLM 전용 고성능 서빙 (PagedAttention) |
| **BentoML** | 모델 패키징 + 서빙 통합 |

---

## 8. MLOps 성숙도 모델 (Google 기준)

| 레벨 | 설명 | 자동화 수준 |
|------|------|------------|
| **Level 0** | 수동 프로세스, Jupyter Notebook | 없음 |
| **Level 1** | ML 파이프라인 자동화 (학습→배포) | 파이프라인 자동화 |
| **Level 2** | CI/CD + 자동 재학습 + 모니터링 | 완전 자동화 |

```
Level 2 MLOps:
  코드 변경 → CI (테스트, 린트) → 파이프라인 빌드
  → 자동 학습 → 모델 검증 → 자동 배포
  → 모니터링 → 성능 저하 감지 → 재학습 트리거
```

---

## 참고 자료

- [MLOps Pipeline: Types, Components & Best Practices (lakeFS)](https://lakefs.io/mlops/mlops-pipeline/)
- [MLOps: CI/CD Pipelines for Model Training and Deployment (Introl)](https://introl.com/blog/mlops-infrastructure-cicd-pipelines-model-training-deployment)
- [MLOps Continuous Delivery and Automation (Google Cloud)](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Model Development and Optimization (Daily Dose of DS)](https://www.dailydoseofds.com/mlops-crash-course-part-8/)
- [MLflow Production Guide](https://www.youngju.dev/blog/ai-platform/2026-03-07-ai-platform-mlflow-experiment-tracking-model-registry.en)
- [MLflow vs Weights & Biases (ZenML)](https://www.zenml.io/blog/mlflow-vs-weights-and-biases)
- [MLOps Frameworks (Databricks)](https://www.databricks.com/blog/mlops-frameworks-complete-guide-tools-and-platforms-production-ml)
