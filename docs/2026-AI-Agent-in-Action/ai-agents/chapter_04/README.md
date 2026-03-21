# Chapter 04: 멀티 에이전트 프레임워크 - AutoGen과 CrewAI

## 환경 설정

의존성 충돌을 방지하기 위해 uv로 프로젝트 전용 가상환경을 생성하여 사용한다.

```bash
# 설치 (가상환경 생성 + 의존성 설치)
make install

# AutoGen Studio 실행
make autogen

# 가상환경 삭제
make clean
```

개별 스크립트 실행 시:

```bash
.venv/bin/python autogen_start.py
```

---

## 개요

이 챕터에서는 멀티 에이전트 시스템을 구축하기 위한 두 가지 주요 프레임워크인 **AutoGen**과 **CrewAI**를 실습한다. 단일 에이전트의 한계를 넘어, 여러 에이전트가 협업하여 코드 작성, 코드 리뷰, 품질 검증 등 복잡한 작업을 수행하는 방법을 다룬다. 또한 AgentOps를 활용한 에이전트 모니터링과 GPT-4 Vision을 이용한 이미지 분석 기능도 함께 살펴본다.

---

## 파일 설명

### AutoGen 관련 파일

| 파일명 | 설명 |
|--------|------|
| `autogen_start.py` | AutoGen 입문 예제. `ConversableAgent`와 `UserProxyAgent`를 사용하여 가장 기본적인 대화 흐름을 구성한다. 사용자 대리 에이전트가 어시스턴트에게 Pygame 스네이크 게임 작성을 요청하는 단순한 구조이다. |
| `autogen_coding_critic.py` | 엔지니어 에이전트와 코드 리뷰어 에이전트를 분리 구성한 예제. `register_nested_chats`를 활용하여 엔지니어가 코드를 작성하면 자동으로 리뷰어가 코드를 검토하는 중첩 대화 패턴을 구현한다. |
| `autogen_coding_critic_cache.py` | 위 `autogen_coding_critic.py`에 디스크 캐시(`Cache.disk`)를 추가한 버전. LLM 호출 결과를 캐싱하여 반복 실행 시 비용과 시간을 절약하는 방법을 보여준다. |
| `autogen_coding_group.py` | `GroupChat`과 `GroupChatManager`를 활용한 그룹 채팅 예제. 사용자, 엔지니어, 비평가(Critic) 세 에이전트가 하나의 그룹 채팅 안에서 자유롭게 대화하며 게임 코드를 작성하고 평가한다. 비평가는 버그, 게임플레이, 목표 준수, 미적 요소 등 다차원 평가 점수를 부여한다. |

### CrewAI 관련 파일

| 파일명 | 설명 |
|--------|------|
| `crewai_introduction.py` | CrewAI 입문 예제. 농담 연구자(Joke Researcher)와 농담 작가(Joke Writer) 두 에이전트로 구성된 Crew가 순차적으로 작업을 수행하여 AI 엔지니어 농담을 생성한다. 결과는 `the_best_joke.md` 파일로 출력된다. |
| `crewai_agentops.py` | 위 `crewai_introduction.py`에 AgentOps 모니터링을 추가한 버전. `agentops.init()`을 통해 에이전트 실행 과정을 추적하고 분석할 수 있다. |
| `crewai_coding_crew.py` | 시니어 엔지니어, QA 엔지니어, 수석 QA 엔지니어 세 에이전트로 구성된 코딩 Crew. 순차적 프로세스(`Process.sequential`)로 코드 작성, 오류 검사, 최종 검증 단계를 거치며 게임을 개발한다. |
| `crewai_hierarchy.py` | `crewai_coding_crew.py`와 동일한 에이전트 구성이지만 계층적 프로세스(`Process.hierarchical`)를 사용한다. 매니저 LLM(`ChatOpenAI`)이 작업 배분과 에이전트 간 조율을 자동으로 관리하는 방식을 보여준다. |

### 기타 파일

| 파일명 | 설명 |
|--------|------|
| `describe_image.py` | GPT-4 Vision API를 사용하여 이미지를 분석하고 설명하는 유틸리티 함수. 이미지를 base64로 인코딩하여 API에 전송하는 방식을 구현한다. 에이전트에 도구(tool)로 연결하여 활용할 수 있다. |
| `OAI_CONFIG_LIST.sample` | AutoGen에서 사용하는 LLM 설정 파일의 샘플. OpenAI API와 Azure OpenAI API 모두를 지원하는 구성 예시를 포함한다. 실제 사용 시 API 키를 입력하고 파일명에서 `.sample`을 제거해야 한다. |
| `requirements.txt` | 프로젝트 의존성 목록. `autogenstudio`, `pyautogen`, `crewai[tools]`, `python-dotenv`, `langchain` 패키지를 포함한다. |
| `the_best_joke.md` | CrewAI 농담 생성 Crew의 실행 결과 파일. AI 엔지니어를 주제로 한 농담이 저장되어 있다. |

---

## 핵심 개념

### AutoGen 핵심 개념
- **ConversableAgent / AssistantAgent**: LLM 기반으로 대화하고 작업을 수행하는 에이전트
- **UserProxyAgent**: 사용자를 대리하는 에이전트로, 코드 실행 환경(`code_execution_config`)을 설정할 수 있음
- **중첩 대화 (Nested Chats)**: `register_nested_chats`를 통해 특정 트리거 조건에서 별도의 대화를 자동 실행하는 패턴
- **그룹 채팅 (GroupChat)**: 여러 에이전트가 하나의 대화 공간에서 자유롭게 상호작용하는 구조
- **디스크 캐시 (Cache.disk)**: LLM 응답을 로컬에 캐싱하여 동일 요청의 반복 호출을 방지

### CrewAI 핵심 개념
- **Agent**: 역할(role), 목표(goal), 배경(backstory)으로 정의되는 작업 수행 주체
- **Task**: 설명(description)과 기대 출력(expected_output)으로 정의되는 작업 단위
- **Crew**: 에이전트와 태스크를 묶어 하나의 팀으로 구성하는 단위
- **순차적 프로세스 (Process.sequential)**: 태스크를 정의된 순서대로 실행
- **계층적 프로세스 (Process.hierarchical)**: 매니저 LLM이 작업 배분과 에이전트 조율을 자동 관리
- **위임 (allow_delegation)**: 에이전트가 다른 에이전트에게 작업을 위임할 수 있는지 여부

### 공통 개념
- **AgentOps**: 에이전트 실행 과정을 모니터링하고 추적하는 도구
- **GPT-4 Vision**: 이미지를 입력받아 분석하고 설명하는 멀티모달 기능

---

## 학습 교훈

1. **단일 에이전트보다 멀티 에이전트가 효과적인 경우가 있다.** 코드 작성과 코드 리뷰를 별도의 에이전트로 분리하면 각 에이전트가 자신의 역할에 집중할 수 있어 결과물의 품질이 향상된다. 하나의 에이전트에 모든 책임을 부여하면 역할 간 충돌이 발생할 수 있다.

2. **프레임워크 선택은 작업 특성에 따라 달라진다.** AutoGen은 에이전트 간 자유로운 대화와 코드 실행에 강점이 있고, CrewAI는 역할 기반의 구조화된 워크플로우 정의에 강점이 있다. 두 프레임워크의 차이를 이해하고 상황에 맞게 선택하는 것이 중요하다.

3. **캐싱은 개발 과정에서 필수적이다.** LLM 호출은 비용이 발생하고 응답 시간이 길기 때문에, 개발 및 디버깅 단계에서 `Cache.disk`와 같은 캐싱 메커니즘을 활용하면 효율성을 크게 높일 수 있다.

4. **순차적 프로세스와 계층적 프로세스는 서로 다른 장단점이 있다.** 순차적 프로세스는 흐름이 명확하고 예측 가능하지만, 계층적 프로세스는 매니저가 상황에 따라 유연하게 작업을 배분할 수 있다. 작업의 복잡도와 에이전트 간 의존성에 따라 적절한 방식을 선택해야 한다.

5. **에이전트의 시스템 프롬프트 설계가 결과 품질을 좌우한다.** 비평가(Critic) 에이전트에 다차원 평가 기준(버그, 게임플레이, 목표 준수, 미적 요소)을 명시하면 더 체계적이고 유용한 피드백을 얻을 수 있다. 에이전트의 역할과 기대 행동을 구체적으로 정의할수록 좋은 결과를 얻는다.

6. **모니터링 도구를 초기부터 도입하는 것이 좋다.** AgentOps와 같은 모니터링 도구를 초기 단계부터 통합하면, 에이전트의 동작을 추적하고 문제를 조기에 발견할 수 있어 디버깅 시간을 크게 줄일 수 있다.

7. **멀티모달 기능은 에이전트의 활용 범위를 넓힌다.** `describe_image.py`와 같이 이미지 분석 기능을 도구로 만들어 에이전트에 연결하면, 텍스트뿐 아니라 시각적 정보까지 처리할 수 있는 에이전트를 구축할 수 있다.
