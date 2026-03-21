# Chapter 2 - LLM API 연동과 프롬프트 엔지니어링

OpenAI 호환 API를 활용하여 LLM에 연결하고, 프롬프트 엔지니어링 기법을 실습하는 챕터입니다.

## 환경 설정

```bash
pip install -r requirements.txt
```

`.env` 파일에 아래 환경변수를 설정합니다:

```env
MSA_LLM_API_BASE=http://10.10.20.92:8009/v1
MSA_LLM_MODEL=/models/gpt-oss-120b
MSA_LLM_API_KEY=your-secure-api-key-here
```

## 파일 목록

| 파일 | 용도 | 설명 |
|------|------|------|
| `connecting.py` | LLM 기본 연결 | OpenAI API에 최초 연결하고 단일 질문을 보내 응답을 받는 가장 기본적인 예제. API 키 로딩, 클라이언트 생성, chat completions 호출 흐름을 익힌다. |
| `message_history.py` | 대화 히스토리 활용 | 멀티턴 대화(system/user/assistant 메시지 배열)를 구성하여 LLM에 전달하는 방법을 보여준다. 응답의 전체 JSON 구조(`model_dump`)도 출력하여 API 응답 형식을 확인할 수 있다. |
| `json_output.py` | JSON 형식 응답 | `response_format={"type": "json_object"}`를 사용하여 LLM이 항상 JSON으로 응답하도록 강제하는 방법을 실습한다. 구조화된 출력이 필요한 상황에서 활용한다. |
| `prompt_engineering.py` | 프롬프트 엔지니어링 실습 | `prompts/` 디렉토리의 다양한 프롬프트 전략(구분자, 페르소나, 예시 제공, 단계 지정 등)을 선택·실행하는 대화형 러너. 여러 기법을 비교 실험할 수 있다. |
| `prompt_utils.py` | 공통 유틸리티 | `prompt_llm()` 함수를 제공하는 공유 모듈. 환경변수(`MSA_LLM_API_BASE`, `MSA_LLM_MODEL`, `MSA_LLM_API_KEY`)를 읽어 자동으로 LLM 서버에 연결하며, 파라미터로 직접 지정도 가능하다. |
| `lmstudio_server.py` | 로컬 LLM 연결 | LM Studio 로컬 서버(`localhost:1234`)에 연결하는 예제. 외부 API 없이 로컬 환경에서 LLM을 테스트할 때 사용한다. |

## 프롬프트 전략 (`prompts/`)

`prompt_engineering.py`에서 선택하여 실행할 수 있는 프롬프트 기법들:

| 파일 | 전략 |
|------|------|
| `adopting_personas.jsonl` | 페르소나 부여 - LLM에 특정 역할을 부여하여 응답 스타일을 조절 |
| `detailed_queries.jsonl` | 상세 질의 - 구체적이고 명확한 질문으로 정확한 답변 유도 |
| `provide_examples.jsonl` | 예시 제공 (Few-shot) - 입출력 예시를 함께 제공하여 원하는 형식 유도 |
| `specify_output_length.jsonl` | 출력 길이 지정 - 응답의 길이나 분량을 제어 |
| `specifying_steps.jsonl` | 단계 지정 - 작업을 단계별로 나누어 체계적 응답 유도 |
| `using_delimiters.jsonl` | 구분자 활용 - 삼중 따옴표 등 구분자로 입력 텍스트 영역을 명확히 분리 |

## 학습 포인트

### 1. OpenAI 호환 API의 범용성

`connecting.py` → `lmstudio_server.py` → `prompt_utils.py` 순서로 코드를 비교하면, **동일한 OpenAI SDK로 OpenAI, 로컬 LLM, 사내 LLM 서버 모두 연결**할 수 있다는 것을 알 수 있다. `base_url`과 `api_key`만 바꾸면 되므로, 코드 변경 없이 다양한 LLM 백엔드를 교체할 수 있다.

### 2. 메시지 구조의 이해 (Role 시스템)

`message_history.py`를 통해 Chat Completions API의 핵심 구조를 배운다:
- **system**: LLM의 행동 규칙과 페르소나 설정
- **user**: 사용자 입력
- **assistant**: 이전 대화의 LLM 응답 (대화 맥락 유지)

이 세 가지 role의 조합이 모든 프롬프트 엔지니어링의 기반이 된다.

### 3. 구조화된 출력의 중요성

`json_output.py`에서 `response_format={"type": "json_object"}`를 사용하면 LLM이 항상 파싱 가능한 JSON을 반환한다. 이는 **LLM 출력을 프로그램이 후처리해야 하는 실제 애플리케이션**(에이전트, 파이프라인 등)에서 필수적인 기법이다.

### 4. 프롬프트 엔지니어링 6가지 핵심 전략

`prompt_engineering.py`와 `prompts/` 디렉토리를 통해 체계적으로 비교 실험할 수 있다:

| 전략 | 핵심 교훈 |
|------|----------|
| 단계 지정 | 복잡한 작업을 분해하면 정확도가 올라간다 (Chain of Thought의 기초) |
| 출력 길이 제어 | 분량을 명시하지 않으면 LLM은 과도하게 긴 응답을 생성한다 |
| 예시 제공 (Few-shot) | 원하는 형식을 말로 설명하는 것보다 예시 하나가 더 효과적이다 |
| 구분자 활용 | 지시문과 데이터를 분리해야 프롬프트 인젝션을 방지할 수 있다 |
| 상세 질의 | 모호한 질문은 모호한 답변을 낳는다 — 구체성이 품질을 결정한다 |
| 페르소나 부여 | 동일한 질문도 역할에 따라 완전히 다른 관점의 답변이 나온다 |

### 5. 공통 유틸리티 패턴

`prompt_utils.py`는 환경변수 기반으로 설정을 주입하는 패턴을 보여준다. 이 방식은:
- API 키를 코드에 하드코딩하지 않아 **보안**에 유리
- `.env` 파일만 바꾸면 **환경별 전환**(개발/스테이징/운영)이 간편
- 다른 스크립트에서 `from prompt_utils import prompt_llm`으로 **재사용** 가능

이 패턴은 이후 챕터에서 에이전트를 구축할 때도 동일하게 적용된다.
