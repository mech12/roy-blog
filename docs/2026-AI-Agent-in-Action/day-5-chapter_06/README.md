# Chapter 06: 행동 트리(Behavior Tree)와 AI 에이전트

## 개요

이 챕터는 **행동 트리(Behavior Tree)** 를 활용한 AI 에이전트 설계를 다룹니다. 게임 AI에서 출발한 행동 트리 패턴을 `py_trees` 라이브러리로 구현하고, 점진적으로 **Semantic Kernel**과 결합하여 LLM 기반 에이전트의 의사결정 구조를 만드는 과정을 학습합니다.

### 핵심 개념

| 개념 | 설명 |
|------|------|
| **Selector** | 자식 노드 중 하나라도 SUCCESS이면 성공 (OR 논리, 우선순위 결정) |
| **Sequence** | 모든 자식 노드가 SUCCESS여야 성공 (AND 논리, 단계별 실행) |
| **Blackboard** | 노드 간 데이터를 공유하는 게시판 (READ/WRITE 권한 기반) |
| **Decorator** | 기존 노드를 감싸서 재시도, 반전 등 부가 기능 추가 |
| **Guard** | 실행 전 유효성 검증 (Pre-condition 체크) |
| **Reactive** | 긴급 상황 시 우선순위 가로채기 (memory=False 활용) |

---

## 학습 순서 및 파일 설명

### 1단계: 행동 트리 기초

| 파일 | 설명 |
|------|------|
| `first_btree.py` | 행동 트리 입문. 사과/배 먹기 예제로 Selector와 Sequence의 기본 동작을 학습. 조건(Condition) 노드와 행동(Action) 노드의 차이를 이해. |
| `second_btree.py` | 스마트홈 비서 시나리오. 전원 확인 -> 온도 체크 -> 에어컨 가동의 Sequence와, 실패 시 창문 환기로 전환하는 Selector 패턴 실습. |

### 2단계: 행동 트리 심화

| 파일 | 설명 |
|------|------|
| `행동트리1.py` | 스마트 팩토리 온도 모니터링. `tick_once()`로 트리를 구동하고, 랜덤 온도에 따라 경고음을 발생시키는 기본 시나리오. `memory=False` 설정으로 매 틱마다 처음부터 평가. |
| `행동트리2.py` | 팩토리 시나리오 확장. 응급 대응(온도 > 80)과 정상 운영(온도 > 30)의 2단계 우선순위 구성. `unicode_tree()`로 트리 상태 시각화. |
| `행동트리3.py` | **블랙보드(Blackboard)** 도입. 노드 간 `is_hungry` 상태를 공유 게시판으로 전달. READ/WRITE 권한 등록, `memory=True`의 진행 위치 기억 기능 학습. |

### 3단계: 고급 패턴

| 파일 | 설명 |
|------|------|
| `가드.py` | **가드(Guard) 패턴**. API 키 존재 여부를 사전 검증하여, 키가 없으면 후속 작업을 차단하는 Pre-condition 체크 구현. |
| `데코레이터.py` | **데코레이터(Decorator) 패턴**. 불안정한 네트워크 연결 노드에 `Retry` 데코레이터를 적용하여, 로직 수정 없이 최대 5회 재시도 기능 추가. |
| `리액티브.py` | **리액티브(Reactive) 패턴**. `memory=False` Selector로 매 틱마다 화재 센서를 우선 확인. 블랙보드 상태 변경 시 즉시 긴급 대응으로 전환. |
| `시각화.py` | RUNNING/SUCCESS/FAILURE 상태 전환을 `unicode_tree()`로 실시간 시각화. 트리 디버깅 방법 학습. |

### 4단계: Semantic Kernel 통합

| 파일 | 설명 |
|------|------|
| `시맨틱커널_행동트리.py` | Semantic Kernel + 행동 트리 통합 1단계. OpenAI GPT-4o 커널을 생성하고, 이메일 분석(AnalyzeEmail) -> 답장 작성(DraftReply) 시퀀스를 블랙보드 기반으로 구성. `is_urgent` 플래그로 노드 간 비동기 데이터 전달. |
| `시맨틱커널_행동트리2.py` | 통합 2단계. SK로 감정 분석(ANGRY/HAPPY/NEUTRAL) 후, Selector로 감정별 대응 노드를 분기. Sequence 안에 Selector를 중첩하는 복합 트리 구조 실습. |

### 5단계: 설계 원칙

| 파일 | 설명 |
|------|------|
| `재사용의미학.py` | **서브트리 재사용** 패턴. 이메일 수집 서브트리를 함수로 정의하고, 비서 에이전트와 보안 에이전트에서 각각 플러그인하여 재사용. 레고 블록처럼 조립하는 설계 철학. |

### 참고 파일

| 파일 | 설명 |
|------|------|
| `플레이그라운드.txt` | 교재 원본 리포지토리(GPTAssistantsPlayground) 환경 구성 가이드. conda 환경 생성, Prefect v2 설치, Gradio/Pydantic 호환성 설정 등의 메모. |
| `requirements.txt` | 프로젝트 의존성 목록. |

---

## 실행 방법

### 환경 설정

```bash
# conda 환경 생성 (권장)
conda create -n btree python=3.9
conda activate btree

# 의존성 설치
pip install py-trees==2.2.3
pip install openai==1.12.0
pip install semantic-kernel
pip install python-dotenv==1.0.1
```

### 기본 예제 실행

```bash
# 1단계: 기초 예제
python first_btree.py
python second_btree.py

# 2단계: 심화 예제
python 행동트리1.py
python 행동트리2.py
python 행동트리3.py

# 3단계: 고급 패턴
python 가드.py
python 데코레이터.py
python 리액티브.py
python 시각화.py

# 4단계: Semantic Kernel 통합 (OPENAI_API_KEY 환경변수 필요)
export OPENAI_API_KEY="your-api-key"
python 시맨틱커널_행동트리.py
python 시맨틱커널_행동트리2.py

# 5단계: 재사용 패턴
python 재사용의미학.py
```

### 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `py-trees` | 2.2.3 | 행동 트리 프레임워크 |
| `openai` | 1.12.0 | OpenAI API 클라이언트 |
| `semantic-kernel` | latest | Microsoft Semantic Kernel (LLM 오케스트레이션) |
| `python-dotenv` | 1.0.1 | 환경변수 관리 |

---

## 참고 자료

- 교재 원본 리포지토리: https://github.com/cxbxmxcx/GPTAssistantsPlayGround
- py_trees 공식 문서: https://py-trees.readthedocs.io/
