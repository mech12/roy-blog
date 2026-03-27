# NVIDIA Jetson 임베디드 컴퓨팅 환경

## 개요

NVIDIA Jetson은 GPU 가속 병렬 처리를 지원하는 임베디드 AI 컴퓨팅 플랫폼이다. 로봇, 자율주행, 스마트 카메라 등 실시간 AI 추론이 필요한 엣지 디바이스에 최적화되어 있으며, 소형/저전력 모듈과 개발자 키트, 그리고 풍부한 AI 소프트웨어 스택을 제공한다.

---

## 제품 라인업 비교

| 모델 | AI 성능 (TOPS) | 메모리 | 전력 | 폼팩터 |
|------|---------------|--------|------|--------|
| **Jetson Orin Nano 4GB** | 20 | 4GB | 7W | SO-DIMM (69.6 x 45mm) |
| **Jetson Orin Nano 8GB** | 40 | 8GB | 7~25W | SO-DIMM (69.6 x 45mm) |
| **Jetson Orin Nano Super** | 67 | 8GB | 7/15/25W | SO-DIMM (69.6 x 45mm) |
| **Jetson Orin NX 8GB** | 70 | 8GB | 10~25W | SO-DIMM (69.6 x 45mm) |
| **Jetson Orin NX 16GB** | 157 | 16GB | 10~40W | SO-DIMM (69.6 x 45mm) |
| **Jetson AGX Orin 32GB** | 200 | 32GB | ~60W | Molex Mezz 699-pin (100 x 87mm) |
| **Jetson AGX Orin 64GB** | 275 | 64GB | ~75W | Molex Mezz 699-pin (100 x 87mm) |
| **Jetson Thor** (차세대) | 2,070 (FP4) | - | - | 차세대 로보틱스/의료 |

> Jetson Orin Nano Super Developer Kit: $249 / Jetson AGX Orin 64GB Developer Kit: $1,999

---

## 소프트웨어 스택

### JetPack SDK

NVIDIA Jetson 공식 소프트웨어 스택. 최신 **JetPack 7**은 로보틱스 및 생성형 AI를 엣지에서 초저지연/결정적 성능으로 구동하도록 설계되었다.

JetPack에 포함된 주요 구성 요소:

- **CUDA** - GPU 병렬 컴퓨팅 툴킷
- **cuDNN** - 딥러닝 프리미티브 라이브러리
- **TensorRT** - 고성능 추론 런타임 (레이어 퓨전, 정밀도 캘리브레이션, 커널 오토튜닝)
- **VPI (Vision Programming Interface)** - 컴퓨터 비전 가속
- **Multimedia API** - 하드웨어 인코더/디코더 접근
- **L4T (Linux for Tegra)** - BSP(Board Support Package) 및 커널

### DeepStream SDK

GStreamer 기반 스트리밍 분석 툴킷으로, AI 기반 멀티센서 처리(비디오, 오디오, 이미지)에 최적화:

- 실시간 비디오 분석(IVA) 앱/서비스 개발
- TensorRT 최적화 모델 통합
- **컨테이너 배포 지원**: CUDA/TensorRT를 컨테이너 내부에 포함하여 BSP만 설치된 Jetson에서 바로 실행
- Kubernetes + Helm 기반 스케일러블 배포 가능
- "Build once, deploy anywhere" (클라우드, 워크스테이션, Jetson)

### Isaac SDK / Isaac ROS

- 로봇 개발을 위한 AI 프레임워크
- ROS2와 통합하여 자율 로봇 내비게이션, 매니퓰레이션 지원
- DNN 기반 인지(Perception) 파이프라인 제공

---

## 실무 활용 영역

### 자율주행 및 로봇

- 실시간 객체 인식 (TensorRT 최적화 딥러닝 모델)
- 깊이 카메라 기반 사람/장애물 감지
- GPU에서 AI 모델을 직접 실행하여 서버 오프로딩 없이 실시간 추론
- ROS2와 결합한 인지(Perception) → 계획(Planning) → 제어(Control) 파이프라인

### 스마트 비디오 분석

- DeepStream 기반 멀티 카메라 실시간 분석
- 교통 모니터링, 공공 안전, 제조 품질 검사

### 산업용 IoT / 엣지 AI

- 생산 효율 모니터링
- 자산 상태 모니터링
- 의료 시스템 (Jetson Thor 기반)

### 임베디드 LLM / VLM

- 엣지에서 LLM, VLM, 파운데이션 모델 실행
- 로보틱스용 생성형 AI 적용

---

## MLOps 관점에서의 Jetson

### 엣지 디바이스 배포 파이프라인

1. **모델 학습** - 클라우드/서버에서 학습
2. **모델 최적화** - TensorRT로 양자화/최적화
3. **컨테이너 패키징** - Docker + DeepStream 컨테이너
4. **엣지 배포** - K3s/Kubernetes 또는 직접 배포
5. **모니터링** - 엣지 디바이스 성능/추론 결과 모니터링

### 컨테이너 기반 운영

- NGC(NVIDIA GPU Cloud) 컨테이너 레지스트리에서 사전 빌드 이미지 제공
- DeepStream Container Builder로 커스텀 컨테이너 생성
- Kubernetes + Helm 차트로 다수 엣지 디바이스 통합 관리

---

## 참고 자료

- [Jetson Embedded AI Computing Platform](https://developer.nvidia.com/embedded-computing)
- [Jetson Modules Lineup](https://developer.nvidia.com/embedded/jetson-modules)
- [JetPack SDK](https://developer.nvidia.com/embedded/jetpack)
- [DeepStream SDK](https://developer.nvidia.com/deepstream-sdk)
- [Jetson AGX Orin](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/)
- [Jetson Thor](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/)
- [Edge AI on Jetson: LLMs, VLMs, Foundation Models for Robotics](https://developer.nvidia.com/blog/getting-started-with-edge-ai-on-nvidia-jetson-llms-vlms-and-foundation-models-for-robotics/)
- [Jetson 모듈 비교 (Seeed Studio)](https://www.seeedstudio.com/blog/nvidia-jetson-comparison-nano-tx2-nx-xavier-nx-agx-orin/)
- [Orin Module Comparison (Connect Tech)](https://connecttech.com/orin-module-comparison/)
