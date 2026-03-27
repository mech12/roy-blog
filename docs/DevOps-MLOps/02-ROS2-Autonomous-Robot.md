# ROS2 기반 자율주행 및 로봇 시스템

## 개요

ROS2(Robot Operating System 2)는 로봇 소프트웨어 개발을 위한 오픈소스 프레임워크이다. ROS1의 한계(단일 마스터, 실시간 미지원, 보안 부재)를 극복하여 산업용 자율주행 및 로봇 시스템에 적합하도록 재설계되었다.

---

## ROS1 vs ROS2 핵심 차이

| 항목 | ROS1 | ROS2 |
|------|------|------|
| **통신 미들웨어** | 자체 TCPROS/UDPROS | DDS (Data Distribution Service) 산업 표준 |
| **마스터 노드** | roscore 필수 (SPOF) | 분산형, 마스터 불필요 |
| **실시간성** | 미지원 | 실시간 스케줄링 지원 |
| **보안** | 없음 | DDS Security 기반 인증/암호화 |
| **QoS** | 제한적 | DDS QoS 정책 (Reliability, Durability 등) |
| **멀티 플랫폼** | Linux 중심 | Linux, Windows, macOS, RTOS |
| **라이프사이클 관리** | 없음 | Managed Node 라이프사이클 |

---

## 시스템 아키텍처

ROS2 자율주행 시스템은 **SOA(Service-Oriented Architecture)** 원칙에 기반한 경량/모듈형/확장 가능한 구조를 따른다.

### 계층 구조

```
┌─────────────────────────────────────┐
│           Application Layer          │
│  (미션 플래닝, 행동 트리, UI)          │
├─────────────────────────────────────┤
│           Planning Layer             │
│  (경로 계획, 동작 계획, 의사결정)       │
├─────────────────────────────────────┤
│          Perception Layer            │
│  (객체 인식, SLAM, 위치 추정)          │
├─────────────────────────────────────┤
│           Control Layer              │
│  (모터 제어, PID, 액추에이터)           │
├─────────────────────────────────────┤
│          Hardware / Sensor Layer      │
│  (LiDAR, Camera, IMU, GPS, Encoder)  │
└─────────────────────────────────────┘
```

### 핵심 구성 요소

- **Perception (인지)**: 센서 데이터로부터 환경 인식 (LiDAR, 카메라, 레이더)
- **Localization (위치 추정)**: SLAM, AMCL, EKF 등으로 로봇 위치 추정
- **Planning (계획)**: 글로벌/로컬 경로 계획, 장애물 회피
- **Control (제어)**: 모터/액추에이터 제어, 경로 추종

---

## 주요 패키지 및 프레임워크

### Navigation2 (Nav2)

ROS2 공식 내비게이션 스택:

- 글로벌 경로 계획 (Dijkstra, A*, NavFn)
- 로컬 경로 계획 (DWB, TEB, MPPI Controller)
- 코스트맵 (Costmap2D) - 장애물 회피를 위한 환경 지도
- 행동 트리(Behavior Tree) 기반 태스크 관리
- Waypoint Following, Keepout Zones 등

### SLAM Toolbox

- 2D SLAM (GMapping, Cartographer, SLAM Toolbox)
- 3D SLAM (LIO-SAM, RTAB-Map)
- 실시간 지도 생성 및 위치 추정

### Autoware

ROS2 기반 오픈소스 자율주행 소프트웨어 플랫폼:

- 인지, 위치 추정, 계획, 제어 전체 스택 제공
- 실제 차량 배포 검증 완료
- Autoware.Auto → Autoware Universe로 발전

### TF2 (Transform)

- 센서/로봇 프레임 간 좌표 변환 관리
- `base_link`, `odom`, `map` 등 프레임 트리 관리
- 자율주행 시스템에서 센서 퓨전의 기반

---

## 통신 인프라

### DDS (Data Distribution Service)

ROS2의 핵심 통신 미들웨어:

- **Publish-Subscribe** 패턴 기반 비동기 통신
- **QoS 정책**: Reliability(신뢰성), Durability(내구성), Deadline, Liveliness 등
- **DDS 구현체**: Fast DDS (eProsima), Cyclone DDS (Eclipse), Connext DDS (RTI)
- 분산 컴퓨트 노드 간 신뢰성 있는 통신 보장

### 통신 패턴

- **Topic** - 1:N Pub/Sub (센서 데이터 스트리밍)
- **Service** - 1:1 요청/응답 (설정 변경, 상태 조회)
- **Action** - 장기 실행 태스크 + 피드백 (내비게이션 목표)
- **Parameter** - 런타임 파라미터 관리

---

## 개발 도구

| 도구 | 용도 |
|------|------|
| **RViz2** | 3D 시각화 (센서 데이터, TF 트리, 경로, 코스트맵) |
| **Gazebo** | 물리 시뮬레이션 환경 (SIL 테스트) |
| **ros2 bag** | 데이터 기록/재생 (디버깅, 회귀 테스트) |
| **ros2 launch** | 다중 노드 실행 관리 (Python/XML/YAML) |
| **colcon** | 빌드 시스템 (CMake/ament 기반) |
| **rqt** | GUI 기반 디버깅 도구 모음 |

### 클라이언트 라이브러리 (RCL)

- **rclcpp** - C++ (성능 크리티컬 노드)
- **rclpy** - Python (프로토타이핑, 고수준 로직)
- **rcljava** - Java

---

## NVIDIA Jetson + ROS2 통합

### Isaac ROS

NVIDIA가 제공하는 ROS2 하드웨어 가속 패키지:

- GPU 가속 SLAM, 스테레오 비전, 객체 감지
- TensorRT 최적화 DNN 추론 노드
- Jetson 하드웨어에 최적화된 성능

### 배포 구성

```
Jetson AGX Orin / Orin NX
├── JetPack 7 (L4T + CUDA + TensorRT)
├── ROS2 Humble / Jazzy
├── Isaac ROS packages
├── Nav2 + SLAM Toolbox
└── Docker Container (선택)
```

---

## MLOps/DevOps 관점

### CI/CD 파이프라인

- **시뮬레이션 테스트**: Gazebo + ros2 bag 기반 SIL/HIL 테스트
- **컨테이너화**: Docker 기반 ROS2 노드 패키징
- **자동 빌드**: colcon + GitHub Actions / GitLab CI
- **배포**: K3s 또는 직접 배포를 통한 엣지 디바이스 업데이트

### 컨테이너 마이크로서비스 아키텍처

최근 연구에서는 ROS2 노드를 컨테이너화된 마이크로서비스로 분리하여 독립적 배포/스케일링이 가능한 아키텍처가 제안되고 있다.

---

## 참고 자료

- [ROS 2-Based Architecture for Autonomous Driving Systems (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12845773/)
- [Autonomous Driving System Architecture with ROS2 and Adaptive AUTOSAR](https://www.mdpi.com/2079-9292/13/7/1303)
- [A Containerized Microservice Architecture for ROS 2 Autonomous (arXiv)](https://arxiv.org/pdf/2404.12683)
- [A Self-Driving Car Architecture in ROS2 (IEEE)](https://ieeexplore.ieee.org/document/9041020/)
- [ROS1과 ROS2의 구조적 차이와 자율주행 시스템 비교분석 (고려대)](https://nmlab.korea.ac.kr/publication/published.papers/2025/2025.04_Comparison_of_ROS1_and_ROS2-KNOM2025.pdf)
- [자율주행 로봇을 위한 ROS 2 & SLAM & Nav2 (WikiDocs)](https://wikidocs.net/book/18444)
- [ROS2 로보틱스 엔지니어링 (러닝스푼즈)](https://learningspoons.com/course/detail/ros2/)
- [How to Build Autonomous Mobile Robots with NVIDIA Jetson](https://www.xavor.com/blog/autonomous-robot-with-nvidia-jetson-overview/)
