# DevOps (Development Operations)

개발(Development)과 운영(Operations)을 통합하여 소프트웨어의 **빌드 → 테스트 → 배포 → 운영**을 자동화하고 지속적으로 개선하는 문화이자 엔지니어링 프랙티스.

---

## 핵심 원칙: CALMS

| 원칙 | 설명 |
|------|------|
| **C**ulture | 개발과 운영의 벽을 허무는 협업 문화 |
| **A**utomation | 반복 작업의 자동화 (빌드, 테스트, 배포) |
| **L**ean | 낭비 제거, 작은 단위로 빠르게 전달 |
| **M**easurement | 메트릭 기반 의사결정 (DORA 지표 등) |
| **S**haring | 지식과 책임의 공유 |

---

## DevOps 라이프사이클 (무한루프)

```
        Plan → Code → Build → Test
          ↑                       ↓
       Monitor ← Operate ← Deploy ← Release
```

```
┌──────────────────────────────────────────────┐
│              DevOps ∞ Loop                   │
│                                              │
│   ┌─ DEV ──────────┐  ┌─ OPS ─────────────┐ │
│   │ Plan            │  │ Release           │ │
│   │ Code            │  │ Deploy            │ │
│   │ Build           │  │ Operate           │ │
│   │ Test            │  │ Monitor           │ │
│   └─────────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 각 단계 상세

### ① Plan (계획)

- 요구사항 정의, 백로그 관리, 스프린트 계획
- **도구**: Jira, Linear, GitHub Issues, Notion

### ② Code (개발)

- 피처 브랜치 전략, 코드 리뷰, 페어 프로그래밍
- **도구**: Git, GitHub/GitLab, VS Code

### ③ Build (빌드)

- 소스 코드 컴파일, 의존성 해결, 아티팩트 생성
- **도구**: Maven, Gradle, npm, CMake, Bazel

### ④ Test (테스트)

| 테스트 유형 | 설명 |
|-------------|------|
| Unit Test | 함수/클래스 단위 테스트 |
| Integration Test | 모듈 간 연동 테스트 |
| E2E Test | 전체 시스템 시나리오 테스트 |
| Performance Test | 부하/스트레스 테스트 |
| Security Test | 취약점 스캔 (SAST/DAST) |

- **도구**: pytest, JUnit, Selenium, k6, SonarQube

### ⑤ Release (릴리스)

- 버전 태깅, 릴리스 노트 생성, 아티팩트 레지스트리 등록
- **전략**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **도구**: GitHub Releases, Harbor, Nexus

### ⑥ Deploy (배포)

| 전략 | 설명 |
|------|------|
| Rolling Update | 인스턴스를 순차적으로 교체 |
| Blue/Green | 두 환경을 전환 (무중단) |
| Canary | 소수 트래픽으로 먼저 검증 후 확대 |
| Feature Flag | 코드 배포와 기능 활성화를 분리 |

- **도구**: Argo CD, Flux, Helm, Kustomize

### ⑦ Operate (운영)

- 인프라 프로비저닝, 스케일링, 장애 대응
- **도구**: Kubernetes, Docker, Terraform, Ansible

### ⑧ Monitor (모니터링)

| 영역 | 대상 | 도구 예시 |
|------|------|-----------|
| Metrics | CPU, 메모리, 응답시간 | Prometheus, Grafana |
| Logs | 애플리케이션/시스템 로그 | ELK Stack, Loki |
| Traces | 분산 시스템 요청 추적 | Jaeger, Zipkin |
| Alerting | 임계값 초과 시 알림 | PagerDuty, Alertmanager |

---

## CI/CD 파이프라인

DevOps의 핵심 자동화 메커니즘.

```
┌─── CI (Continuous Integration) ───────────────────┐
│                                                    │
│  git push → Lint → Build → Unit Test → 아티팩트   │
│                                                    │
└────────────────────────────────────────────────────┘
           ↓
┌─── CD (Continuous Delivery) ──────────────────────┐
│                                                    │
│  아티팩트 → Integration Test → Staging 배포 → 승인 │
│                                                    │
└────────────────────────────────────────────────────┘
           ↓
┌─── CD (Continuous Deployment) ────────────────────┐
│                                                    │
│  승인 → Production 배포 → Smoke Test → 모니터링   │
│                                                    │
└────────────────────────────────────────────────────┘
```

### CI/CD 도구 비교

| 도구 | 특징 |
|------|------|
| GitHub Actions | GitHub 네이티브, YAML 기반, 풍부한 마켓플레이스 |
| GitLab CI/CD | GitLab 통합, Auto DevOps 지원 |
| Jenkins | 오픈소스, 플러그인 생태계, 자체 호스팅 |
| Argo CD | Kubernetes 네이티브 GitOps |
| CircleCI | SaaS 기반, 빠른 빌드 |

---

## Infrastructure as Code (IaC)

인프라를 코드로 정의하고 버전 관리하는 프랙티스.

| 도구 | 분류 | 설명 |
|------|------|------|
| Terraform | Provisioning | 클라우드/온프레미스 인프라 선언적 관리 |
| Ansible | Configuration | 서버 설정 자동화 (에이전트리스) |
| Pulumi | Provisioning | 프로그래밍 언어로 인프라 정의 |
| Helm | Packaging | Kubernetes 애플리케이션 패키징 |

---

## 컨테이너 & 오케스트레이션

```
┌─────────────────────────────────────────────┐
│  Container Runtime                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ App A   │ │ App B   │ │ App C   │      │
│  │ + Deps  │ │ + Deps  │ │ + Deps  │      │
│  └─────────┘ └─────────┘ └─────────┘      │
│  Docker / containerd                        │
├─────────────────────────────────────────────┤
│  Orchestration: Kubernetes / K3s            │
│  - 스케줄링, 스케일링, 셀프힐링, 서비스디스커버리 │
└─────────────────────────────────────────────┘
```

---

## DORA 지표 (DevOps 성과 측정)

| 지표 | 설명 | Elite 수준 |
|------|------|------------|
| Deployment Frequency | 배포 빈도 | 하루 여러 번 |
| Lead Time for Changes | 커밋 → 배포 소요 시간 | 1시간 미만 |
| Change Failure Rate | 배포 후 장애 비율 | 5% 미만 |
| Time to Restore | 장애 복구 시간 | 1시간 미만 |

---

## DevOps vs MLOps 비교

| 항목 | DevOps | MLOps |
|------|--------|-------|
| 대상 | 애플리케이션 코드 | 코드 + 데이터 + 모델 |
| 버전 관리 | 코드 (Git) | 코드 + 데이터 + 모델 아티팩트 |
| 테스트 | 유닛/통합/E2E | + 모델 성능/Data Drift |
| 배포 | 서버/컨테이너 | + 엣지 디바이스, 추론 서버 |
| 모니터링 | 시스템 메트릭, 로그 | + 모델 정확도, Data Drift |
| 고유 단계 | - | CT (Continuous Training) |
| 피드백 루프 | 사용자 → 개발자 | 운영 데이터 → 재학습 → 재배포 |

---

## whereable.ai DevOps 포지션과의 연결

채용 공고 기준 핵심 DevOps 스택:

```
CI/CD          → GitHub Actions
컨테이너        → Docker
오케스트레이션   → K3s (경량 Kubernetes, 온프레미스/엣지)
IaC            → Bash/Python 스크립트 자동화
DB HA          → PostgreSQL + Patroni (Raft 합의)
네트워크        → WireGuard VPN, STUN/TURN
모니터링        → Prometheus, Grafana, ELK Stack
```

온프레미스 환경(공항, 군수시설)에서 클라우드 없이 자체 인프라를 구축·운영해야 하므로, IaC와 자동화 스크립팅 역량이 특히 중요하다.
