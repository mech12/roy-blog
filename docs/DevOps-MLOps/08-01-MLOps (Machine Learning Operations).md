# MLOps (Machine Learning Operations)

ML 모델을 **개발 → 배포 → 운영 → 개선**하는 전체 라이프사이클을 자동화하고 관리하는 엔지니어링 프랙티스. DevOps의 원칙을 ML 시스템에 적용한 것이다.

---

## 전체 파이프라인 단계

```
┌─────────────────────────────────────────────────────────┐
│                    MLOps Lifecycle                       │
│                                                         │
│  ① Data        ② Model         ③ Deploy      ④ Monitor │
│  ─────────    ──────────      ─────────     ────────── │
│  수집/저장  →  학습/검증   →   배포/서빙  →  모니터링   │
│     ↑                                           │       │
│     └───────────── ⑤ 재학습 (Feedback Loop) ────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## ① Data Pipeline (데이터 파이프라인)

| 단계 | 설명 |
|------|------|
| 데이터 수집 | 센서, 로그, API 등에서 원시 데이터 수집 |
| 데이터 저장 | Data Lake / Data Warehouse에 저장 |
| 데이터 전처리 | 정제, 변환, 피처 엔지니어링 |
| 데이터 검증 | 스키마 검증, 분포 이상 탐지 (Data Drift 감지) |
| 데이터 버전 관리 | DVC, Delta Lake 등으로 데이터셋 버전 추적 |

**도구 예시**: Apache Kafka, Spark, Airflow, DVC, Great Expectations

---

## ② Model Development (모델 개발)

| 단계 | 설명 |
|------|------|
| 실험 추적 | 하이퍼파라미터, 메트릭, 아티팩트 기록 |
| 모델 학습 | GPU/TPU 클러스터에서 분산 학습 |
| 모델 검증 | 테스트셋 평가, A/B 비교 |
| 모델 레지스트리 | 학습된 모델을 버전별로 저장·관리 |

**도구 예시**: MLflow, Weights & Biases, Kubeflow, Neptune

---

## ③ CI/CD/CT (지속적 통합/배포/학습)

기존 DevOps의 CI/CD에 **CT(Continuous Training)**가 추가된 것이 MLOps의 핵심 차별점이다.

### DevOps vs MLOps: CI/CD 비교

| 구분 | DevOps CI/CD | MLOps CI/CD/CT |
|------|-------------|----------------|
| 트리거 | 코드 변경 (git push) | 코드 변경 + **데이터 변경** + **모델 성능 저하** |
| 테스트 대상 | 코드 (단위/통합/E2E) | 코드 + **데이터 검증** + **모델 품질 검증** |
| 빌드 산출물 | 컨테이너 이미지, 바이너리 | 컨테이너 + **학습된 모델 아티팩트** |
| 배포 대상 | 애플리케이션 | 애플리케이션 + **모델** |

### CI / CD / CT 상세

```
CI (Continuous Integration)
  └─ 코드 + 데이터 + 모델 변경 시 자동 테스트
     · 코드 린트, 유닛 테스트
     · 데이터 스키마 검증 (Great Expectations 등)
     · 모델 학습 코드 검증 (소규모 데이터셋으로 빠른 학습 테스트)

CD (Continuous Delivery/Deployment)
  └─ 검증된 모델을 자동으로 프로덕션에 배포
     · 모델 레지스트리에서 승인된 모델을 서빙 인프라에 배포
     · Canary / Blue-Green / Shadow 배포 전략 적용

CT (Continuous Training)  ← MLOps 고유
  └─ 새 데이터 또는 성능 저하 감지 시 자동으로 모델 재학습
```

### CT가 필요한 이유

일반 소프트웨어는 코드가 바뀌지 않으면 동작이 변하지 않지만, ML 모델은 **데이터가 바뀌면 성능이 떨어진다.**

```
배포 시점                          시간 경과
  ↓                                  ↓
모델 정확도 95% ──────────────────→ 정확도 80% ❌
                  Data Drift 발생
                  (입력 데이터 분포 변화)

CT 파이프라인이 있으면:
모델 정확도 95% ───→ 80% 감지 → 자동 재학습 → 94% ✅
```

### CT 트리거 조건

| 트리거 | 설명 | 예시 |
|--------|------|------|
| 스케줄 기반 | 주기적으로 재학습 | 매일/매주 cron |
| 데이터 기반 | 새 데이터가 일정량 쌓이면 | 10만 건 신규 데이터 |
| 성능 기반 | 모니터링 지표가 임계값 이하로 떨어지면 | 정확도 < 90% |
| 드리프트 기반 | Data/Concept Drift 감지 시 | 입력 분포 변화 탐지 |

### CT 파이프라인 흐름

```
 모니터링 알림 (성능 저하/Drift 감지)
         │
         ▼
 ┌───────────────┐
 │ 새 데이터 수집  │
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ 데이터 검증    │ ← 스키마, 분포, 이상치 체크
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ 모델 재학습    │ ← 기존 파이프라인 자동 실행
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ 모델 검증     │ ← 기존 모델 대비 성능 비교
 └───────┬───────┘
         ▼
    성능 향상? ──No──→ 기존 모델 유지, 알림
         │
        Yes
         ▼
 ┌───────────────┐
 │ 모델 레지스트리 │ ← 새 버전 등록
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │  CD로 자동 배포 │ ← Canary/Shadow 배포
 └───────────────┘
```

**도구 예시**: GitHub Actions, Jenkins, Argo CD, Tekton, Kubeflow Pipelines, Vertex AI Pipelines

---

## ④ Model Serving (모델 서빙/배포)

| 방식 | 설명 | 적용 예 |
|------|------|---------|
| REST/gRPC API | 실시간 추론 요청 처리 | 웹 서비스 |
| Batch Inference | 대량 데이터 일괄 추론 | 야간 배치 처리 |
| Edge Deployment | 임베디드 디바이스에 모델 탑재 | 자율주행차 (Jetson) |
| Streaming | 실시간 스트림 데이터 추론 | IoT 센서 |

**도구 예시**: TensorRT, ONNX Runtime, Triton Inference Server, TFLite, KServe

---

## ⑤ Monitoring & Feedback (모니터링 및 피드백)

| 항목 | 설명 |
|------|------|
| Model Performance | 정확도, 지연시간 등 추론 품질 추적 |
| Data Drift | 입력 데이터 분포 변화 감지 |
| Concept Drift | 데이터와 예측 간 관계 변화 감지 |
| System Metrics | CPU/GPU 사용률, 메모리, 처리량 |
| Alerting | 성능 저하 시 알림 → 자동 재학습 트리거 |

**도구 예시**: Prometheus, Grafana, Evidently AI, WhyLabs

---

## MLOps 성숙도 수준 (Google 기준)

| Level | 이름 | 설명 |
|-------|------|------|
| 0 | Manual | 수동 학습, 수동 배포 (Jupyter에서 실험) |
| 1 | ML Pipeline Automation | 학습 파이프라인 자동화, CT 도입 |
| 2 | CI/CD Pipeline Automation | 코드+데이터+모델 전체 CI/CD/CT 자동화 |

---

## whereable.ai DevOps/MLOps 포지션과의 연결

채용 공고의 요구사항을 MLOps 단계에 매핑하면:

```
데이터 수집     → ROS2 센서 데이터 (카메라, LiDAR)
모델 학습       → 월드 모델 E2E 학습 (GPU 클러스터)
CI/CD/CT       → GitHub Actions 파이프라인
모델 서빙       → Jetson Edge 배포 (K3s + Docker)
인프라          → 온프레미스 K8s, PostgreSQL HA (Patroni)
모니터링        → Prometheus, Grafana, ELK Stack
네트워크        → WireGuard VPN (차량 ↔ 관제 서버)
```

이 회사에서는 특히 **Edge 배포**(Level 2 수준의 자동화)와 **온프레미스 인프라 운영**이 핵심 챌린지가 될 것이다.
