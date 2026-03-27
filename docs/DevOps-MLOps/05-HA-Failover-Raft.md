# 무중단 서비스 운영 (High Availability & Failover)

> 다른 분야 시니어 엔지니어를 위한 핵심 용어 해설 포함

---

## 1. 핵심 개념 정리

### 고가용성 (High Availability, HA)

**한 줄 요약**: "시스템 장애가 발생해도 서비스가 중단되지 않는 것"

| 가용성 수준 | 연간 허용 다운타임 | 설명 |
|------------|-------------------|------|
| 99% (two nines) | 3.65일 | 낮은 수준 |
| 99.9% (three nines) | 8.77시간 | 일반 서비스 |
| 99.99% (four nines) | 52.6분 | 높은 수준 |
| 99.999% (five nines) | 5.26분 | 금융/통신 수준 |

### SPOF (Single Point of Failure)

**한 줄 요약**: "하나가 죽으면 전체가 죽는 지점"

```
SPOF 있음                        SPOF 제거
┌──────┐                        ┌──────┐ ┌──────┐
│ App  │                        │ App1 │ │ App2 │
└──┬───┘                        └──┬───┘ └──┬───┘
   │                               │        │
┌──▼───┐ ← 이게 죽으면 끝       ┌──▼────────▼──┐
│  DB  │                        │ DB Primary   │
└──────┘                        │     ↕ 복제    │
                                │ DB Replica   │
                                └──────────────┘
```

### 페일오버 (Failover)

**한 줄 요약**: "Primary가 죽으면 자동으로 Replica가 역할을 인수하는 것"

```
정상 상태:
  Client → Primary DB (읽기/쓰기)
            ↓ 복제
           Replica DB (읽기 전용)

장애 발생:
  Client → Primary DB ✗ (장애!)
            ↓
  자동 감지 → Replica DB가 Primary로 승격 (페일오버)
            ↓
  Client → 새 Primary DB (구 Replica)
```

---

## 2. 분산 합의 알고리즘

### 왜 합의 알고리즘이 필요한가?

여러 서버(노드)가 "누가 리더인지", "어떤 데이터가 최신인지" 합의해야 함.
합의 없이 각자 판단하면 **Split-Brain**(두 노드가 동시에 자신이 리더라고 주장) 발생 → 데이터 불일치

### Raft 합의 알고리즘

**한 줄 요약**: "분산 시스템에서 노드들이 리더를 선출하고, 데이터 변경을 합의하는 프로토콜"

Paxos와 동일한 안전성을 보장하면서도 이해하기 쉽게 설계됨.

#### 세 가지 역할

| 역할 | 설명 |
|------|------|
| **Leader** | 클라이언트 요청을 받아 로그를 복제하는 유일한 노드 |
| **Follower** | Leader의 로그를 복제/저장하며 투표에 참여 |
| **Candidate** | Leader가 응답 없을 때 새 선거를 시작하는 노드 |

#### 동작 원리

**1단계: 리더 선출 (Leader Election)**

```
초기 상태: 모든 노드가 Follower
           각 노드는 랜덤 타임아웃 설정

타임아웃 만료:  Node A → Candidate로 전환
               "나를 리더로 투표해주세요" (RequestVote RPC)

투표:          Node B → "찬성" (자기 텀에 아직 투표 안했으면)
               Node C → "찬성"

과반수 획득:    Node A → Leader 확정! (3/5 이상 = 과반)
               Heartbeat 주기적 전송 시작
```

**2단계: 로그 복제 (Log Replication)**

```
Client: "X=5로 변경해줘"
         ↓
Leader:  로그에 기록 "X=5" (uncommitted)
         → Follower들에게 전파 (AppendEntries RPC)
         ↓
Follower: 로그에 기록 "X=5" (uncommitted)
          → "받았어" 응답
         ↓
Leader:  과반수 응답 수신 → Commit!
         → Follower들에게 "커밋해" 통보
         → Client에게 "성공" 응답
```

**3단계: 장애 복구**

```
Leader 장애 발생:
  Follower들의 Heartbeat 타임아웃 만료
  → 가장 먼저 타임아웃된 노드가 Candidate
  → 새 선거 시작
  → 새 Leader 선출 (보통 수 초 이내)
```

#### 핵심 보장 사항

- **과반수(Quorum)**: 5노드 클러스터 → 3노드만 살아있으면 동작 가능 (2대 장애 허용)
- **단일 리더**: 한 시점에 반드시 1명의 Leader만 존재
- **로그 일관성**: 커밋된 로그는 모든 노드에서 동일한 순서

---

## 3. etcd

### etcd란?

**한 줄 요약**: "Raft 기반의 분산 키-값 저장소 (Kubernetes의 뇌)"

```
etcd 클러스터 (3 또는 5노드)
┌─────────┐     ┌─────────┐     ┌─────────┐
│ etcd-0  │ ←→  │ etcd-1  │ ←→  │ etcd-2  │
│ (Leader)│     │(Follower)│    │(Follower)│
└─────────┘     └─────────┘     └─────────┘
     ↑
  Kubernetes API Server가 여기에
  클러스터 상태를 저장/조회
```

### 주요 용도

| 시스템 | etcd 역할 |
|--------|----------|
| **Kubernetes** | 모든 클러스터 상태 저장 (Pod, Service, ConfigMap 등) |
| **Patroni** | PostgreSQL 클러스터의 리더 선출 및 상태 관리 |
| **CoreDNS** | 서비스 디스커버리 정보 저장 |

### 핵심 특성

- **강한 일관성**: 읽기/쓰기 모두 일관성 보장 (linearizable)
- **Watch 기능**: 키 변경을 실시간 감지 (이벤트 기반)
- **TTL/Lease**: 키에 만료 시간 설정 가능 → 리더 Lease에 활용
- **권장 노드 수**: 3 (1대 장애 허용) 또는 5 (2대 장애 허용) — 항상 홀수

---

## 4. Patroni — PostgreSQL HA

### Patroni란?

**한 줄 요약**: "PostgreSQL 클러스터의 고가용성을 자동으로 관리하는 도구"

```
┌─ Patroni 아키텍처 ──────────────────────────────────┐
│                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │ etcd-0  │←→ │ etcd-1  │←→ │ etcd-2  │          │
│  └────┬────┘    └────┬────┘    └────┬────┘          │
│       │              │              │                │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐          │
│  │Patroni-0│    │Patroni-1│    │Patroni-2│          │
│  │   +     │    │   +     │    │   +     │          │
│  │PG Primary│   │PG Replica│   │PG Replica│         │
│  │(읽기/쓰기)│  │(읽기전용) │   │(읽기전용) │         │
│  └─────────┘    └─────────┘    └─────────┘          │
│       ↑                                              │
│  ┌────┴────┐                                         │
│  │ HAProxy │ ← Client 연결 (항상 Primary로 라우팅)     │
│  └─────────┘                                         │
└──────────────────────────────────────────────────────┘
```

### 동작 원리

1. **리더 Lease**: Primary 노드가 etcd에 주기적으로 리더 Lease 갱신
2. **Lease 만료**: Primary가 Lease 갱신 실패 → etcd에서 리더 키 삭제
3. **선출**: 가장 데이터가 최신인 Replica가 새 리더로 선출
4. **승격**: 새 리더가 Primary로 승격 (`pg_ctl promote`)
5. **재구성**: 나머지 Replica들이 새 Primary를 따르도록 자동 재구성
6. **라우팅**: HAProxy가 새 Primary를 감지하고 트래픽 라우팅 변경

### 핵심 용어

| 용어 | 설명 |
|------|------|
| **Streaming Replication** | PostgreSQL의 WAL(Write-Ahead Log)을 실시간으로 Replica에 전송 |
| **WAL (Write-Ahead Log)** | 트랜잭션을 먼저 로그에 기록 → 이후 데이터 파일에 반영 (장애 복구 핵심) |
| **Synchronous Replication** | Replica가 WAL 수신을 확인해야 커밋 완료 (데이터 손실 0, 지연 증가) |
| **Asynchronous Replication** | 커밋 후 비동기로 WAL 전송 (약간의 데이터 손실 가능, 빠름) |
| **Split-Brain** | 2개 노드가 동시에 Primary라고 주장하는 상황 → etcd + Raft로 방지 |
| **Fencing** | 구 Primary를 강제로 읽기 전용으로 전환하여 데이터 불일치 방지 |

### Patroni vs 수동 HA 관리

| 항목 | 수동 관리 | Patroni |
|------|----------|---------|
| 장애 감지 | 모니터링 알림 → 사람이 판단 | 자동 (Heartbeat + Lease) |
| 페일오버 | DBA가 수동으로 Replica 승격 | 자동 (수 초 이내) |
| 복구 후 재합류 | 수동 설정 (pg_basebackup 등) | 자동 (구 Primary → Replica로 재합류) |
| Split-Brain 방지 | 사람 의존 | etcd + Raft로 자동 보장 |

---

## 5. 전체 HA 스택 구성 예시

```
┌─ 클라이언트 ─────────────────────────────────────────────┐
│  App Server (FastAPI / Spring)                           │
└──────────┬───────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────┐
│  HAProxy / PgBouncer (커넥션 풀링 + 로드밸런싱)             │
│  - Primary 포트: 5000 → 읽기/쓰기                         │
│  - Replica 포트: 5001 → 읽기 전용 (부하 분산)               │
└──────────┬───────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────┐
│  PostgreSQL 클러스터 (Patroni 관리)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ PG-0     │  │ PG-1     │  │ PG-2     │                │
│  │ Primary  │──│ Replica  │──│ Replica  │                │
│  │ (R/W)    │  │ (R/O)    │  │ (R/O)    │                │
│  └──────────┘  └──────────┘  └──────────┘                │
└──────────┬───────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────┐
│  etcd 클러스터 (3노드)                                     │
│  - 리더 선출 정보 저장                                      │
│  - 클러스터 상태 관리                                       │
│  - Raft 합의로 일관성 보장                                   │
└──────────────────────────────────────────────────────────┘
```

### 장애 시나리오와 자동 복구

| 장애 | 자동 복구 과정 | 소요 시간 |
|------|--------------|----------|
| Primary DB 다운 | Patroni가 감지 → etcd Lease 만료 → Replica 승격 → HAProxy 재라우팅 | 5~30초 |
| Replica 1대 다운 | 나머지 Replica가 읽기 부하 담당, 자동 복구 대기 | 즉시 |
| etcd 1대 다운 | 3노드 중 2노드로 Quorum 유지 → 정상 동작 | 즉시 |
| 네트워크 파티션 | 과반수 파티션만 동작, 소수 파티션은 읽기 전용으로 전환 | 수 초 |

---

## 참고 자료

- [Raft Consensus Algorithm (공식)](https://raft.github.io/)
- [Patroni Documentation](https://patroni.readthedocs.io/en/latest/README.html)
- [High Availability PostgreSQL with Patroni](https://dev.to/prezaei/high-availability-postgresql-clustering-with-patroni-5043)
- [Percona - Patroni](https://docs.percona.com/postgresql/18/solutions/patroni-info.html)
- [Percona - etcd](https://docs.percona.com/postgresql/18/solutions/etcd-info.html)
- [Raft Algorithm & Backup in ETCD (EzyInfra)](https://ezyinfra.dev/blog/raft-algo-backup-etcd)
- [Patroni Deployment Patterns (PGConf EU 2024)](https://www.postgresql.eu/events/pgconfeu2024/sessions/session/5892/slides/544/patroni-deployment-patterns.pdf)
