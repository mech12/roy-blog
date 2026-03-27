# Kubernetes & 컨테이너 인프라 용어 사전

> 04-01 문서에서 다루는 개념들의 빠른 참조용 용어 사전

---

## 컨테이너 기초

| 용어 | 설명 |
|------|------|
| **Container** | 앱과 의존성을 격리된 환경에서 실행하는 경량 가상화 단위. OS 커널을 호스트와 공유한다 |
| **Image** | 컨테이너 실행에 필요한 파일시스템 + 설정을 담은 읽기 전용 패키지 |
| **Dockerfile** | 이미지를 빌드하기 위한 명령어 스크립트. `FROM`, `RUN`, `COPY`, `CMD` 등으로 구성 |
| **Registry** | 이미지를 저장·배포하는 원격 저장소 (Docker Hub, Harbor, ECR, GCR 등) |
| **Volume** | 컨테이너 라이프사이클과 독립적인 영구 저장소. 컨테이너가 삭제되어도 데이터 보존 |
| **Layer** | 이미지의 각 명령어가 생성하는 파일시스템 변경분. 레이어 캐싱으로 빌드 속도 향상 |
| **OCI** | Open Container Initiative. 컨테이너 이미지/런타임의 업계 표준 규격 |
| **containerd** | Docker에서 분리된 컨테이너 런타임. Kubernetes가 직접 사용하는 CRI 구현체 |

---

## Kubernetes 코어

| 용어 | 설명 |
|------|------|
| **Cluster** | Control Plane + Worker Node들로 구성된 Kubernetes 전체 환경 |
| **Control Plane** | 클러스터를 관리하는 마스터 컴포넌트 집합 (API Server, etcd, Scheduler, Controller Manager) |
| **API Server** | 모든 K8s 요청의 진입점. `kubectl`, 내부 컴포넌트, 외부 시스템 모두 여기를 통한다 |
| **etcd** | 클러스터의 모든 상태를 저장하는 분산 Key-Value 저장소 |
| **Scheduler** | 새로 생성된 Pod를 어느 Node에 배치할지 결정 (리소스, affinity, taint 등 고려) |
| **Controller Manager** | 현재 상태를 선언된 상태(desired state)와 일치시키는 제어 루프 집합 |
| **kubelet** | 각 Worker Node에서 실행되며 Pod의 생성/삭제/상태 보고를 담당하는 에이전트 |
| **kube-proxy** | 각 Node에서 Service의 네트워크 규칙(iptables/IPVS)을 관리하는 네트워크 프록시 |

---

## 워크로드 오브젝트

| 용어 | 설명 |
|------|------|
| **Pod** | K8s의 최소 배포 단위. 1개 이상의 컨테이너가 네트워크/스토리지를 공유 |
| **Node** | Pod가 실행되는 물리/가상 머신. Master Node와 Worker Node로 구분 |
| **Deployment** | Stateless 앱의 선언적 배포/스케일링/롤링 업데이트를 관리하는 컨트롤러 |
| **StatefulSet** | Stateful 앱에 고정된 Pod 이름, 순서 보장, 전용 스토리지를 제공하는 컨트롤러 |
| **DaemonSet** | 모든(또는 특정) Node에 정확히 1개의 Pod를 보장하는 컨트롤러 |
| **ReplicaSet** | 지정된 수의 Pod 복제본을 유지. Deployment가 내부적으로 관리하므로 직접 사용은 드뭄 |
| **Job** | 1회성 작업을 실행하고 완료되면 종료되는 워크로드 (배치 처리, 마이그레이션 등) |
| **CronJob** | Job을 cron 스케줄에 따라 주기적으로 실행 |

---

## 네트워킹

| 용어 | 설명 |
|------|------|
| **Service** | Pod 집합에 안정적인 IP/DNS를 부여하는 추상화. Pod가 재생성되어도 엔드포인트 유지 |
| **ClusterIP** | Service의 기본 타입. 클러스터 내부에서만 접근 가능한 가상 IP |
| **NodePort** | 모든 Node의 특정 포트를 열어 외부에서 접근 가능하게 하는 Service 타입 |
| **LoadBalancer** | 클라우드 프로바이더의 LB를 자동 생성하여 외부 트래픽을 받는 Service 타입 |
| **Ingress** | HTTP/HTTPS 트래픽을 URL 경로/호스트 기반으로 내부 Service에 라우팅하는 규칙 |
| **Ingress Controller** | Ingress 규칙을 실제로 처리하는 리버스 프록시 (Traefik, Nginx 등) |
| **CNI** | Container Network Interface. Pod 간 네트워크를 구성하는 플러그인 규격 (Flannel, Calico 등) |
| **CoreDNS** | 클러스터 내부 DNS 서버. `서비스명.네임스페이스.svc.cluster.local` 형태로 해석 |
| **Namespace** | 리소스를 논리적으로 격리하는 가상 클러스터. 팀/환경별 분리에 사용 |
| **Label** | 리소스에 부착하는 키-값 태그. Service의 Pod 선택, 필터링에 사용 |
| **Annotation** | Label과 유사하지만 선택에 사용되지 않는 메타데이터 (설명, 버전, 도구 설정 등) |

---

## 스토리지

| 용어 | 설명 |
|------|------|
| **PersistentVolume (PV)** | 클러스터 레벨에서 프로비저닝된 저장소 리소스 |
| **PersistentVolumeClaim (PVC)** | 사용자가 PV를 요청하는 선언. Pod는 PVC를 통해 스토리지에 접근 |
| **StorageClass** | 동적 프로비저닝 정책 정의. PVC 생성 시 자동으로 PV를 생성 |
| **accessModes** | 스토리지 접근 모드 — `ReadWriteOnce`(단일 노드), `ReadWriteMany`(다중 노드), `ReadOnlyMany` |
| **CSI** | Container Storage Interface. 외부 스토리지 시스템(NFS, Ceph, EBS 등)을 K8s와 연결하는 규격 |

---

## 설정 및 보안

| 용어 | 설명 |
|------|------|
| **ConfigMap** | 설정값(환경변수, 설정 파일)을 코드와 분리하여 K8s에 저장하는 오브젝트 |
| **Secret** | ConfigMap과 유사하지만 민감 정보(비밀번호, API 키, 인증서) 전용. Base64 인코딩 저장 |
| **RBAC** | Role-Based Access Control. 사용자/서비스 계정에 K8s 리소스 접근 권한을 부여 |
| **ServiceAccount** | Pod에 할당되는 K8s 내부 계정. RBAC 권한을 Pod 단위로 제어 |
| **Taint / Toleration** | Node에 제약(Taint)을 걸고, 특정 Pod만 허용(Toleration)하는 스케줄링 제어 |
| **Affinity** | Pod를 특정 Node에 배치하거나 특정 Pod과 같은/다른 Node에 배치하는 규칙 |

---

## Helm

| 용어 | 설명 |
|------|------|
| **Helm** | Kubernetes 패키지 매니저. 여러 K8s 리소스를 하나의 Chart로 묶어 배포·관리 |
| **Chart** | K8s 리소스 템플릿 + 기본값 + 메타데이터를 패키징한 디렉토리 구조 |
| **values.yaml** | Chart의 기본 설정값 파일. `--set` 또는 `-f` 플래그로 오버라이드 가능 |
| **Release** | Chart를 클러스터에 설치한 인스턴스. 같은 Chart를 여러 Release로 설치 가능 |
| **Repository** | Chart를 저장·공유하는 원격 저장소 (Artifact Hub, Harbor, ChartMuseum 등) |
| **Template** | Go 템플릿 문법으로 K8s YAML을 동적 생성 (`{{ .Values.replicas }}`) |

---

## K3s / 경량 Kubernetes

| 용어 | 설명 |
|------|------|
| **K3s** | Rancher가 만든 경량 K8s 배포판. 단일 바이너리(~100MB), ARM 지원 |
| **K3s Server** | Control Plane 역할. 기본으로 SQLite를 etcd 대신 사용 |
| **K3s Agent** | Worker Node 역할. Server에 연결하여 Pod를 실행 |
| **Traefik** | K3s에 기본 포함된 Ingress Controller. 자동 HTTPS(Let's Encrypt) 지원 |
| **Flannel** | K3s에 기본 포함된 CNI 플러그인. Pod 간 오버레이 네트워크 구성 |
| **K0s** | K3s와 유사한 경량 K8s 배포판. Mirantis가 관리 |
| **MicroK8s** | Canonical(Ubuntu)의 경량 K8s. snap으로 설치 |
| **Kind** | Kubernetes IN Docker. Docker 컨테이너로 K8s 클러스터를 실행 (로컬 테스트용) |

---

## 자주 사용하는 kubectl 명령어

| 명령어 | 설명 |
|--------|------|
| `kubectl get pods` | Pod 목록 조회 |
| `kubectl get pods -o wide` | Pod 목록 + Node/IP 정보 포함 |
| `kubectl describe pod <name>` | Pod 상세 정보 + 이벤트 로그 |
| `kubectl logs <pod>` | Pod의 컨테이너 로그 출력 |
| `kubectl exec -it <pod> -- bash` | Pod 내부 셸 접속 |
| `kubectl apply -f <file>` | YAML 파일의 리소스를 생성/업데이트 (선언적) |
| `kubectl delete -f <file>` | YAML 파일의 리소스 삭제 |
| `kubectl get all -n <ns>` | 특정 Namespace의 모든 리소스 조회 |
| `kubectl top nodes` | Node별 CPU/메모리 사용량 (metrics-server 필요) |
| `kubectl rollout status deployment/<name>` | Deployment 롤아웃 상태 확인 |
| `kubectl rollout undo deployment/<name>` | Deployment를 이전 버전으로 롤백 |
