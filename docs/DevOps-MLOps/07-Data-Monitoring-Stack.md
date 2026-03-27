# 데이터 관리 및 모니터링 스택

> 다른 분야 시니어 엔지니어를 위한 핵심 용어 해설 포함

---

## 1. 실시간 데이터 스트리밍

### Apache Kafka

**한 줄 요약**: "대규모 실시간 데이터 파이프라인을 위한 분산 이벤트 스트리밍 플랫폼"

#### 핵심 개념

```
Producer (생산자)              Kafka Cluster                Consumer (소비자)
┌──────────┐                  ┌─ Topic: "orders" ──┐       ┌──────────┐
│ 주문 서비스│ ── 메시지 ──→   │ Partition 0: [1,4,7]│ ──→  │ 분석 서비스│
│          │                  │ Partition 1: [2,5,8]│ ──→  │ 알림 서비스│
│ 결제 서비스│ ── 메시지 ──→   │ Partition 2: [3,6,9]│ ──→  │ DB 동기화 │
└──────────┘                  └────────────────────┘       └──────────┘
```

| 용어 | 설명 | 비유 |
|------|------|------|
| **Producer** | 메시지를 Kafka에 보내는 클라이언트 | 택배 발송인 |
| **Consumer** | 메시지를 Kafka에서 읽는 클라이언트 | 택배 수령인 |
| **Topic** | 메시지 카테고리 (논리적 채널) | 우체국의 사서함 |
| **Partition** | Topic을 분할한 순서 보장 단위 | 사서함을 여러 칸으로 나눔 |
| **Broker** | Kafka 서버 인스턴스 | 우체국 지점 |
| **Consumer Group** | 같은 Topic을 분담 처리하는 Consumer 집합 | 팀으로 택배 나눠 처리 |
| **Offset** | Partition 내 메시지의 순번 | 택배 송장번호 |
| **Replication** | Partition을 여러 Broker에 복제 | 백업 사서함 |

#### 기존 메시지 큐(RabbitMQ)와의 차이

| 항목 | RabbitMQ (메시지 큐) | Kafka (이벤트 스트림) |
|------|---------------------|---------------------|
| **메시지 보관** | 소비 후 삭제 | 설정 기간 동안 영구 보관 |
| **재처리** | 불가 | Offset 되감기로 재처리 가능 |
| **처리량** | 수만 msg/s | 수백만 msg/s |
| **순서 보장** | 큐 단위 | Partition 단위 |
| **용도** | 작업 큐, RPC | 이벤트 소싱, 로그 수집, 데이터 파이프라인 |

#### 실무 활용 사례

- **로그 수집**: 서비스 로그 → Kafka → Elasticsearch (실시간 검색)
- **이벤트 소싱**: 사용자 행동 이벤트 → Kafka → 실시간 추천/분석
- **데이터 동기화**: DB 변경 → Kafka (CDC) → 다른 서비스/DB
- **ML 피처 파이프라인**: 원시 데이터 → Kafka → Feature 계산 → Feature Store

### CDC (Change Data Capture)

**한 줄 요약**: "DB 변경 사항을 실시간으로 스트리밍하는 기술"

```
PostgreSQL → Debezium (CDC) → Kafka → Elasticsearch / 다른 DB
  INSERT/UPDATE/DELETE가         변경 이벤트를    여러 소비자가
  발생할 때마다                    Kafka에 기록     실시간 수신
```

---

## 2. 대규모 데이터 처리

### Apache Spark

**한 줄 요약**: "대규모 분산 데이터 처리 엔진 (배치 + 실시간)"

#### 핵심 개념

```
┌─ Spark 아키텍처 ────────────────────────────────────┐
│                                                      │
│  Driver Program                                      │
│  ┌────────────────┐                                  │
│  │ SparkContext   │                                  │
│  │ (작업 분배)     │                                  │
│  └───────┬────────┘                                  │
│          │                                           │
│  ┌───────▼────┐  ┌────────────┐  ┌────────────┐     │
│  │ Executor 1 │  │ Executor 2 │  │ Executor 3 │     │
│  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │     │
│  │ │ Task 1 │ │  │ │ Task 3 │ │  │ │ Task 5 │ │     │
│  │ │ Task 2 │ │  │ │ Task 4 │ │  │ │ Task 6 │ │     │
│  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │     │
│  └────────────┘  └────────────┘  └────────────┘     │
│                                                      │
│  데이터를 여러 노드에 분산하여 병렬 처리                  │
└──────────────────────────────────────────────────────┘
```

| 용어 | 설명 | 비유 |
|------|------|------|
| **RDD** | Resilient Distributed Dataset, 분산 불변 데이터셋 | 분산된 배열 |
| **DataFrame** | 구조화된 분산 데이터 (SQL과 유사) | 분산 테이블 |
| **Transformation** | 데이터 변환 (map, filter, join) — Lazy 평가 | SQL의 SELECT/WHERE |
| **Action** | 결과를 반환하는 연산 (count, collect, save) | SQL 실행 |
| **Partition** | 데이터를 분할한 병렬 처리 단위 | 테이블 샤드 |
| **Shuffle** | 파티션 간 데이터 재분배 (join, groupBy 시 발생) | 정렬/재배치 (비용 높음) |

#### Spark 구성 요소

| 구성 요소 | 용도 |
|----------|------|
| **Spark SQL** | 구조화된 데이터 처리 (SQL 쿼리 지원) |
| **Spark Streaming** | 마이크로배치 기반 실시간 처리 |
| **Structured Streaming** | DataFrame API 기반 실시간 처리 (더 높은 수준) |
| **MLlib** | 분산 머신러닝 라이브러리 |
| **GraphX** | 그래프 처리 |

#### Kafka + Spark 연동 예시

```python
# Spark Structured Streaming + Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "user-events") \
    .load()

# 실시간 집계
result = df.groupBy(
    window("timestamp", "5 minutes"),
    "event_type"
).count()

# 결과를 다시 Kafka 또는 DB에 저장
result.writeStream \
    .format("kafka") \
    .option("topic", "event-aggregates") \
    .start()
```

---

## 3. 시스템 모니터링

### Prometheus

**한 줄 요약**: "시계열 메트릭 수집/저장/쿼리 시스템"

```
┌─ Prometheus 아키텍처 ──────────────────────────────────┐
│                                                         │
│  ┌────────────┐  Pull (HTTP)   ┌───────────────┐       │
│  │ App Server │ ◄───────────── │  Prometheus   │       │
│  │ :8080/metrics│              │  Server       │       │
│  └────────────┘                │  ┌──────────┐ │       │
│                                │  │ TSDB     │ │       │
│  ┌────────────┐  Pull          │  │(시계열DB) │ │       │
│  │ Node       │ ◄───────────── │  └──────────┘ │       │
│  │ Exporter   │                │  ┌──────────┐ │       │
│  │ :9100/metrics│              │  │ PromQL   │ │       │
│  └────────────┘                │  │(쿼리엔진) │ │       │
│                                │  └──────────┘ │       │
│  ┌────────────┐  Pull          │  ┌──────────┐ │       │
│  │ DB         │ ◄───────────── │  │Alertmgr  │ │       │
│  │ Exporter   │                │  │(알림관리) │ │       │
│  └────────────┘                │  └──────────┘ │       │
│                                └───────────────┘       │
└─────────────────────────────────────────────────────────┘
```

#### 핵심 용어

| 용어 | 설명 | 비유 |
|------|------|------|
| **Metric** | 시간에 따라 변하는 수치 데이터 | 체온 측정값 |
| **Exporter** | 앱/시스템의 메트릭을 Prometheus 형식으로 노출하는 에이전트 | 체온계 |
| **Pull 모델** | Prometheus가 주기적으로 대상에서 메트릭을 가져옴 | Prometheus가 직접 방문 |
| **TSDB** | Time Series Database, 시계열 데이터 전용 저장소 | 시간별 기록장 |
| **PromQL** | Prometheus Query Language | SQL for 메트릭 |
| **Alertmanager** | 조건 충족 시 Slack/Email/PagerDuty 등으로 알림 | 비상 알림 시스템 |

#### 메트릭 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| **Counter** | 단조 증가 카운터 (리셋 시에만 0) | 요청 수, 에러 수 |
| **Gauge** | 오르내리는 현재값 | CPU 사용률, 메모리, 온도 |
| **Histogram** | 값의 분포 (버킷별 카운트) | 응답 시간 분포 |
| **Summary** | 슬라이딩 윈도우 기반 분위수 | P95 응답 시간 |

#### PromQL 예시

```promql
# CPU 사용률 (5분 평균)
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# HTTP 에러율 (5xx)
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m])) * 100

# 디스크 사용량 80% 이상인 노드 (Alert 조건)
node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.2
```

### Grafana

**한 줄 요약**: "메트릭/로그/트레이스를 시각화하는 대시보드 플랫폼"

- Prometheus, Elasticsearch, InfluxDB 등 다양한 데이터소스 연결
- 대시보드를 JSON으로 정의 → 버전 관리 가능
- 알림 규칙 설정 가능 (Grafana Alerting)
- 커뮤니티 대시보드 공유 (Grafana.com)

```
데이터소스들                  Grafana
┌────────────┐              ┌──────────────────────┐
│ Prometheus │ ──────────→  │ ┌──────┐ ┌──────┐   │
│            │              │ │ CPU  │ │Memory│   │
├────────────┤              │ │ 그래프│ │ 그래프│   │
│ Elasticsearch│ ────────→  │ ├──────┤ ├──────┤   │
│            │              │ │ Disk │ │ QPS  │   │
├────────────┤              │ │ 게이지│ │ 차트 │   │
│ Loki       │ ──────────→  │ └──────┘ └──────┘   │
└────────────┘              └──────────────────────┘
                               웹 브라우저로 접속
```

---

## 4. 로그 관리

### ELK Stack

**한 줄 요약**: "로그 수집 → 저장/검색 → 시각화 파이프라인"

```
ELK Stack 아키텍처
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ App Logs    │   │ Beats /     │   │ Logstash    │   │Elasticsearch│
│ Syslog      │ → │ Filebeat    │ → │ (가공/변환)  │ → │ (저장/검색)  │
│ Access Log  │   │ (수집/전송)  │   │             │   │             │
└─────────────┘   └─────────────┘   └─────────────┘   └──────┬──────┘
                                                              │
                                                     ┌────────▼──────┐
                                                     │   Kibana      │
                                                     │ (시각화/검색)  │
                                                     └───────────────┘
```

| 구성 요소 | 역할 | 비유 |
|----------|------|------|
| **Elasticsearch** | 분산 검색/분석 엔진 (JSON 문서 저장) | Google 검색 엔진 (내부용) |
| **Logstash** | 데이터 수집 + 파싱 + 변환 파이프라인 | ETL 도구 |
| **Kibana** | 데이터 시각화 및 탐색 대시보드 | Grafana (로그 특화) |
| **Beats (Filebeat)** | 경량 로그 수집 에이전트 (서버에 설치) | 로그 택배기사 |

#### Elasticsearch 핵심 용어

| 용어 | 설명 | RDBMS 비유 |
|------|------|-----------|
| **Index** | 문서의 논리적 모음 | Database / Table |
| **Document** | JSON 형식의 개별 데이터 단위 | Row |
| **Field** | Document 내의 키-값 쌍 | Column |
| **Shard** | Index를 분할한 물리적 단위 (분산 저장) | Partition |
| **Replica** | Shard의 복제본 (장애 대비) | Replica |
| **Inverted Index** | 단어 → 문서 ID 역방향 매핑 (빠른 전문 검색) | Full-text Index |

### Loki (Grafana Loki)

- ELK의 경량 대안으로 주목
- 로그 본문을 인덱싱하지 않고 레이블만 인덱싱 → 저장 비용 대폭 절감
- Grafana와 자연스럽게 통합
- LogQL로 쿼리 (PromQL과 유사한 문법)

---

## 5. 알림 (Alerting) 및 자동 복구

### 알림 전략

```
메트릭 수집 → 조건 평가 → 알림 발송 → 자동 복구 (선택)

예시 알림 규칙:
┌──────────────────────────────────────────────────────┐
│ IF cpu_usage > 90% FOR 5분                           │
│   → Slack 채널에 경고 알림                             │
│                                                      │
│ IF disk_usage > 85%                                  │
│   → PagerDuty 호출 (온콜 엔지니어에게 전화)              │
│                                                      │
│ IF http_error_rate > 5% FOR 2분                      │
│   → 자동 롤백 트리거 (이전 버전으로 배포)                 │
│                                                      │
│ IF pod_restart_count > 3 in 10분                     │
│   → Slack 알림 + 자동 스케일업                          │
└──────────────────────────────────────────────────────┘
```

### 주요 알림 채널

| 채널 | 용도 |
|------|------|
| **Slack / Teams** | 팀 채널에 경고/정보 수준 알림 |
| **PagerDuty / OpsGenie** | 온콜 로테이션, 에스컬레이션 (긴급) |
| **Email** | 비긴급 알림, 일일 리포트 |
| **Webhook** | 자동화 트리거 (자동 복구, 스크립트 실행) |

### 자동 복구 전략

| 전략 | 설명 | 도구 |
|------|------|------|
| **Auto-restart** | 프로세스/Pod 자동 재시작 | Kubernetes liveness probe, systemd |
| **Auto-scaling** | 부하에 따라 인스턴스 수 자동 조절 | K8s HPA, KEDA |
| **Auto-failover** | Primary 장애 시 Replica 자동 승격 | Patroni, Redis Sentinel |
| **Auto-rollback** | 배포 후 에러율 증가 시 이전 버전으로 롤백 | Argo Rollouts, Flagger |
| **Self-healing** | 노드 장애 시 다른 노드로 워크로드 재배치 | Kubernetes scheduler |

---

## 6. 통합 모니터링 아키텍처 예시

```
┌─ 서비스 레이어 ──────────────────────────────────────────┐
│  App 1, App 2, App 3 ...                                │
│  각 앱에서:                                               │
│   - /metrics 엔드포인트 노출 (Prometheus)                   │
│   - 로그를 stdout으로 출력 (Docker logging)                  │
│   - 트레이스 전송 (Jaeger/OpenTelemetry)                    │
└──────────┬─────────────────────────────┬────────────────┘
           │                             │
     ┌─────▼─────┐                ┌──────▼──────┐
     │Prometheus │                │  Filebeat   │
     │(메트릭 수집)│               │ (로그 수집)   │
     └─────┬─────┘                └──────┬──────┘
           │                             │
     ┌─────▼─────┐                ┌──────▼──────┐
     │Prometheus │                │Elasticsearch│
     │  TSDB     │                │ (로그 저장)   │
     └─────┬─────┘                └──────┬──────┘
           │                             │
     ┌─────▼─────────────────────────────▼──────┐
     │              Grafana                      │
     │  ┌─────────┐  ┌─────────┐  ┌──────────┐  │
     │  │메트릭    │  │ 로그     │  │ 알림 규칙 │  │
     │  │대시보드  │  │ 탐색     │  │ (Slack)  │  │
     │  └─────────┘  └─────────┘  └──────────┘  │
     └───────────────────────────────────────────┘
```

### Observability의 세 기둥

| 기둥 | 도구 | 답하는 질문 |
|------|------|-----------|
| **Metrics** (메트릭) | Prometheus + Grafana | "시스템이 지금 어떤 상태?" |
| **Logs** (로그) | ELK / Loki | "무슨 일이 일어났는가?" |
| **Traces** (트레이스) | Jaeger / Tempo | "요청이 어디서 느려졌는가?" |

---

## 참고 자료

- [실시간 파생 데이터 생성: Kafka + Spark (SK Planet)](https://techtopic.skplanet.com/sparkstreaming/)
- [Centralized Kafka Monitoring (SPITHA TechBlog)](https://medium.com/spitha-techblog/centralized-monitoring-aed2a95f97d3)
- [ELK vs Grafana vs Prometheus (Last9)](https://last9.io/blog/elk-vs-grafana-vs-prometheus/)
- [Kafka Monitoring with Prometheus and Grafana](https://medium.com/@rramiz.rraza/kafka-metrics-integration-with-prometheus-and-grafana-14fe318fbb8b)
- [Kafka + ELK + Prometheus (GitHub)](https://github.com/6a6aQth/AI-Database-with-Kafka-ELK-Stack-n-Prometheus)
- [Kafka KRaft Monitoring with Prometheus](https://gsfl3101.medium.com/kafka-kraft-monitoring-with-prometheus-and-grafana-1994ef272f48)
