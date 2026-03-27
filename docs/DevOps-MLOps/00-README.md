# DevOps / MLOps 직무 조사

## 목차

| # | 주제 | 세부 문서 |
| --- | ------ | ----------- |
| 01 | NVIDIA Jetson 임베디드 환경 | [01-NVIDIA-Jetson-Embedded.md](01-NVIDIA-Jetson-Embedded.md) |
| 02 | ROS2 기반 자율주행 로봇 시스템 | [02-ROS2-Autonomous-Robot.md](02-ROS2-Autonomous-Robot.md) |
| 03 | 네트워크 / NAT / VPN | [03-Network-NAT-VPN.md](03-Network-NAT-VPN.md) |
| 04 | Kubernetes 컨테이너 인프라 | [04-Kubernetes-Container-Infra.md](04-Kubernetes-Container-Infra.md) |
| 05 | HA / Failover / Raft | [05-HA-Failover-Raft.md](05-HA-Failover-Raft.md) |
| 06 | ML/DL 파이프라인 및 MLOps | [06-MLDL-Pipeline-MLOps.md](06-MLDL-Pipeline-MLOps.md) |
| 07 | 데이터 모니터링 스택 | [07-Data-Monitoring-Stack.md](07-Data-Monitoring-Stack.md) |

---

## MLOps 시스템 설계 및 구축

- 자율주행 소프트웨어 및 머신러닝 모델의 테스트, 배포, 모니터링을 위한 [파이프라인 구축](06-MLDL-Pipeline-MLOps.md)
- Git, Github 등을 활용한 코드 버전 관리 및 CI/CD 파이프라인 설계
- [ROS2 기반 자율주행 시스템](02-ROS2-Autonomous-Robot.md)과의 연동 고려

## 인프라 및 클러스터 관리

- Docker 기반 컨테이너 환경 구축 및 운영
- [Kubernetes 환경 구성 및 관리](04-Kubernetes-Container-Infra.md)
  - K3s 또는 온프레미스 Kubernetes 클러스터를 활용한 서비스 배포
- PostgreSQL 기반 SPOF 없는 분산 SQL DB 시스템 구축
  - Patroni와 같은 도구를 통한 [Raft 합의 알고리즘 기반 자동 페일오버](05-HA-Failover-Raft.md) 구성

## 네트워크 및 자동화 인프라 구축

- [STUN/TURN, VPN 및 WireGuard를 활용한 안정적인 서버 간 통신 및 NAT 환경 극복](03-Network-NAT-VPN.md)
- Bash 및 Python 스크립트를 이용한 인프라 자동화 및 관리

## 임베디드 및 로봇 시스템

- [NVIDIA Jetson 시리즈 등 임베디드 컴퓨팅 환경](01-NVIDIA-Jetson-Embedded.md)에 대한 실무 경험
- [ROS2 기반 자율주행 및 로봇 시스템](02-ROS2-Autonomous-Robot.md) 전반에 대한 이해와 프로젝트 수행 경험

## 데이터 및 모니터링

- [빅데이터 처리, 분산 데이터베이스, 실시간 데이터 스트리밍 및 시스템 모니터링](07-Data-Monitoring-Stack.md)
- Prometheus, Grafana, ELK Stack 등을 활용한 로그 수집 및 분석
- 분산 시스템의 상태 모니터링과 장애 대응을 위한 Alerting 및 자동 복구 전략 수립
