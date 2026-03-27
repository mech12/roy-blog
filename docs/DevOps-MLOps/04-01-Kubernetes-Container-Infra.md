# Kubernetes 및 컨테이너 네이티브 인프라 구축

> 다른 분야 시니어 엔지니어를 위한 핵심 용어 해설 포함

---

## 1. 컨테이너 기초 개념

### 컨테이너 vs 가상머신

```
가상머신 (VM)                    컨테이너 (Docker)
┌─────────┬─────────┐           ┌─────────┬─────────┐
│  App A  │  App B  │           │  App A  │  App B  │
├─────────┼─────────┤           ├─────────┼─────────┤
│ Guest OS│ Guest OS│           │  Libs A │  Libs B │
├─────────┴─────────┤           ├─────────┴─────────┤
│   Hypervisor      │           │   Container Engine │
├───────────────────┤           │   (Docker)         │
│   Host OS         │           ├───────────────────┤
├───────────────────┤           │   Host OS (커널공유)│
│   Hardware        │           ├───────────────────┤
└───────────────────┘           │   Hardware        │
                                └───────────────────┘
 각 VM마다 OS 전체 포함           OS 커널을 공유 → 경량/빠름
 수 GB, 수 분 부팅               수 MB, 수 초 시작
```

### Docker 핵심 용어

| 용어 | 설명 | 비유 |
|------|------|------|
| **Image** | 앱 + 의존성을 패키징한 읽기 전용 템플릿 | 클래스 (설계도) |
| **Container** | 이미지를 실행한 인스턴스 | 객체 (인스턴스) |
| **Dockerfile** | 이미지 빌드 레시피 | Makefile |
| **Registry** | 이미지 저장소 (Docker Hub, Harbor 등) | Maven Repository |
| **Volume** | 컨테이너 외부 영구 저장소 | 외장하드 |
| **Network** | 컨테이너 간 통신 네트워크 | VLAN |

---

## 2. Kubernetes (K8s) 핵심 개념

### Kubernetes란?

**한 줄 요약**: "컨테이너화된 앱의 배포, 스케일링, 운영을 자동화하는 오케스트레이션 플랫폼"

```
클러스터 구조
┌─ Control Plane (마스터) ──────────────────┐
│  API Server    ← kubectl 명령 수신       │
│  etcd          ← 클러스터 상태 저장 (KV DB) │
│  Scheduler     ← Pod를 어느 노드에 배치?    │
│  Controller    ← 원하는 상태 유지 관리       │
└──────────────────────────────────────────┘
        │
┌───────┼───────────────────────┐
│       ▼                       │
│  ┌─ Worker Node 1 ──┐  ┌─ Worker Node 2 ──┐
│  │  kubelet         │  │  kubelet         │
│  │  kube-proxy      │  │  kube-proxy      │
│  │  ┌─Pod──┐ ┌─Pod─┐│  │  ┌─Pod──┐ ┌─Pod─┐│
│  │  │ App  │ │ DB  ││  │  │ App  │ │ App ││
│  │  └──────┘ └─────┘│  │  └──────┘ └─────┘│
│  └──────────────────┘  └──────────────────┘
└───────────────────────────────┘
```

### 핵심 오브젝트 용어 해설

| 용어 | 설명 | 비유 |
|------|------|------|
| **Pod** | 1개 이상의 컨테이너를 묶은 최소 배포 단위 | 프로세스 그룹 |
| **Node** | Pod가 실행되는 물리/가상 서버 | 서버 1대 |
| **Namespace** | 리소스를 논리적으로 격리하는 가상 클러스터 | 프로젝트/폴더 |
| **Service** | Pod 집합에 대한 안정적인 네트워크 엔드포인트 | 로드밸런서 + DNS |
| **Ingress** | 외부 HTTP/HTTPS 트래픽을 클러스터 내부로 라우팅 | 리버스 프록시 (nginx) |
| **Label** | 리소스에 붙이는 키-값 태그 (선택/필터링용) | 태그/카테고리 |

---

## 3. 워크로드 컨트롤러 비교

### Deployment (배포)

**한 줄 요약**: "상태가 없는(stateless) 앱을 선언적으로 배포/관리"

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
spec:
  replicas: 3           # 항상 3개 Pod 유지
  selector:
    matchLabels:
      app: web
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
```

- Pod가 죽으면 자동으로 새 Pod 생성 (어느 노드든 상관없음)
- Pod 이름이 랜덤 (`web-server-abc123`, `web-server-xyz789`)
- **롤링 업데이트**: 이미지 변경 시 하나씩 교체하여 무중단 배포
- **용도**: 웹 서버, API 서버, 마이크로서비스

### StatefulSet (상태유지 집합)

**한 줄 요약**: "상태가 있는(stateful) 앱에 고정된 ID와 저장소를 보장"

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: "postgres"
  replicas: 3
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:16
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:        # 각 Pod마다 별도 PV 자동 생성
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

**Deployment와의 핵심 차이**:

| 항목 | Deployment | StatefulSet |
|------|-----------|-------------|
| **Pod 이름** | 랜덤 (`app-abc123`) | 순서 보장 (`postgres-0`, `postgres-1`, `postgres-2`) |
| **생성/삭제 순서** | 동시 | 순차적 (0→1→2 생성, 2→1→0 삭제) |
| **네트워크 ID** | 변경됨 | 고정 DNS (`postgres-0.postgres.default.svc`) |
| **저장소** | 공유 또는 없음 | 각 Pod마다 전용 PersistentVolume |
| **용도** | 웹 서버, API | DB, Kafka, Elasticsearch, ZooKeeper |

### DaemonSet (데몬 집합)

**한 줄 요약**: "모든 노드에 정확히 1개씩 Pod를 실행"

- 노드가 추가되면 자동으로 Pod 배치, 제거되면 자동 삭제
- **용도**: 로그 수집기 (Fluentd, Filebeat), 모니터링 에이전트 (node-exporter), 네트워크 플러그인

---

## 4. 스토리지

### PersistentVolume (PV) & PersistentVolumeClaim (PVC)

**한 줄 요약**: "Pod와 독립적으로 존재하는 영구 저장소"

```
관리자가 PV 생성           개발자가 PVC로 요청        Pod에서 마운트
┌──────────┐            ┌──────────┐           ┌──────────┐
│ PV 100Gi │ ◄── 바인딩 ─│ PVC 50Gi │ ◄── 사용 ─│ Pod      │
│ (NFS)    │            │          │           │ /data    │
└──────────┘            └──────────┘           └──────────┘
```

| 용어 | 설명 |
|------|------|
| **PV** | 클러스터 레벨의 저장소 리소스 (관리자가 프로비저닝) |
| **PVC** | 사용자(개발자)가 저장소를 요청하는 선언 |
| **StorageClass** | 동적 프로비저닝 정책 (요청 시 자동으로 PV 생성) |
| **accessModes** | `ReadWriteOnce` (단일 노드), `ReadWriteMany` (다중 노드), `ReadOnlyMany` |

### Pod가 삭제되어도 PV의 데이터는 보존됨 → DB에 필수

---

## 5. 설정 관리

### ConfigMap

**한 줄 요약**: "앱 설정값을 코드와 분리하여 Kubernetes에 저장"

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: "postgres-0.postgres"
  LOG_LEVEL: "info"
  max_connections: "100"
```

- 환경변수로 주입하거나 파일로 마운트 가능
- 이미지 재빌드 없이 설정 변경 가능
- **민감 정보는 Secret 사용** (Base64 인코딩, 외부 KMS 연동 가능)

### Secret

- ConfigMap과 유사하지만 민감 정보 전용 (비밀번호, API 키, 인증서)
- etcd에 암호화 저장 가능
- RBAC으로 접근 제어

---

## 6. Helm 차트

### Helm이란?

**한 줄 요약**: "Kubernetes의 패키지 매니저 (apt/yum의 K8s 버전)"

```
Helm 없이                       Helm 사용
├── deployment.yaml              helm install my-app ./my-chart \
├── service.yaml                   --set replicas=3 \
├── configmap.yaml                 --set image.tag=v2.1
├── ingress.yaml                 → 모든 YAML을 템플릿으로 한번에 관리
├── pvc.yaml
└── 5개 파일을 각각 kubectl apply
```

### 핵심 개념

| 용어 | 설명 |
|------|------|
| **Chart** | Kubernetes 리소스 템플릿 패키지 (디렉토리 구조) |
| **values.yaml** | 차트의 기본 설정값 (replicas, image, ports 등) |
| **Release** | 차트를 클러스터에 설치한 인스턴스 |
| **Repository** | 차트 저장소 (Artifact Hub, 사내 Harbor 등) |
| **Template** | Go 템플릿 문법으로 YAML 생성 (`{{ .Values.replicas }}`) |

```
my-chart/
├── Chart.yaml          # 차트 메타데이터 (이름, 버전)
├── values.yaml         # 기본 설정값
├── templates/
│   ├── deployment.yaml # {{ .Values.image.tag }} 등 템플릿
│   ├── service.yaml
│   └── configmap.yaml
└── charts/             # 의존성 하위 차트
```

---

## 7. K3s — 경량 Kubernetes

### K3s란?

**한 줄 요약**: "엣지/IoT/소규모 환경을 위한 경량 Kubernetes 배포판"

| 항목 | 일반 K8s (kubeadm) | K3s |
|------|-------------------|-----|
| **바이너리 크기** | ~1GB+ | ~100MB (단일 바이너리) |
| **메모리** | 2GB+ | 512MB~1GB |
| **etcd** | 별도 클러스터 필요 | 내장 SQLite (또는 외부 DB) |
| **설치** | 복잡 (kubeadm init, join) | `curl -sfL get.k3s.io \| sh -` (1줄) |
| **인증서 관리** | 수동 | 자동 |
| **기본 포함** | 없음 | Traefik Ingress, CoreDNS, Helm Controller, Flannel CNI |

### K3s가 적합한 환경

- NVIDIA Jetson 같은 ARM 기반 엣지 디바이스
- 온프레미스 소규모 클러스터 (3~10대)
- CI/CD 파이프라인 테스트 환경
- 개발/스테이징 환경

---

## 8. 온프레미스 배포 아키텍처 예시

```
┌─ K3s 클러스터 (온프레미스) ───────────────────────────────┐
│                                                          │
│  ┌─ Master Node ─┐  ┌─ Worker 1 ──┐  ┌─ Worker 2 ──┐   │
│  │ k3s server    │  │ k3s agent   │  │ k3s agent   │   │
│  │ API Server    │  │             │  │             │   │
│  │ SQLite/etcd   │  │ ┌─────────┐ │  │ ┌─────────┐ │   │
│  │               │  │ │ App Pod │ │  │ │ App Pod │ │   │
│  │ Traefik       │  │ ├─────────┤ │  │ ├─────────┤ │   │
│  │ (Ingress)     │  │ │ DB Pod  │ │  │ │ DB Pod  │ │   │
│  │               │  │ │(PV:NFS) │ │  │ │(PV:NFS) │ │   │
│  └───────────────┘  │ └─────────┘ │  │ └─────────┘ │   │
│                      └────────────┘  └────────────┘   │
│                                                          │
│  Helm으로 배포: PostgreSQL, App, Monitoring 등             │
└──────────────────────────────────────────────────────────┘
```

---

## 참고 자료

- [StatefulSets (Kubernetes 공식)](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [StatefulSet Basics (Kubernetes Tutorial)](https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/)
- [K3s Deployments vs StatefulSets vs DaemonSets (Stakater)](https://www.stakater.com/post/k8s-deployments-vs-statefulsets-vs-daemonsets)
- [Helm in K3s (공식 문서)](https://docs.k3s.io/add-ons/helm)
- [StatefulSets & Persistent Storage in Kubernetes](https://www.glukhov.org/post/2025/11/statefulsets-and-persistent-storage-in-kubernetes/)
- [Kubernetes StatefulSet vs Deployment (Spacelift)](https://spacelift.io/blog/statefulset-vs-deployment)
