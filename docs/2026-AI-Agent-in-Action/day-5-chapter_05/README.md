# Chapter 05 - Semantic Kernel 기초

Microsoft Semantic Kernel(SK)을 활용한 AI 에이전트 개발 실습 자료입니다.
OpenAI Function Calling 기초부터 SK의 플러그인 시스템, Native/Semantic 함수 연동, 대화형 챗봇까지 단계별로 다룹니다.

> 본 자료는 [`docs/2026-AI-Agent-in-Action/ai-agents/chapter_05`](../ai-agents/chapter_05)의 원본 코드를 강의용으로 수정 및 보강한 버전입니다.

## 환경 설정

- Python 3.10 권장 (conda 환경)
- 필수 패키지: `requirements.txt` 참조 (`openai`, `python-dotenv`, `semantic-kernel`)
- 설치: `make install` (uv 사용)
- 설치 가이드: `시맨틱커널 설치.txt` (소스 클론 방식 포함)

### API 설정 (.env)

`.env.example`을 복사하여 `.env` 파일을 생성하고, 사용할 LLM 엔드포인트를 설정합니다.

```bash
cp .env.example .env
```

**OpenAI API 사용 시:**
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_MODEL=gpt-4o
# OPENAI_API_BASE 미설정 시 기본 OpenAI 엔드포인트 사용
```

**한라02 Qwen3.5-122B (사내 GPU 서버) 사용 시:**
```env
OPENAI_API_KEY=none
OPENAI_API_MODEL=Qwen3.5-122B-A10B-FP8
OPENAI_API_BASE=http://10.10.20.20:8000/v1
```

> 모든 스크립트는 `OPENAI_API_BASE`, `OPENAI_API_MODEL`, `OPENAI_API_KEY` 환경변수를 공통으로 참조합니다.
> OpenAI-compatible API(vLLM, Ollama 등)라면 어떤 엔드포인트든 사용할 수 있습니다.

## 파일 구성

### 1. OpenAI Function Calling 기초

| 파일 | 설명 |
|------|------|
| `first_function.py` | OpenAI Function Calling 기본 구조 - 함수 설계도(tools) 정의 및 호출 여부 판단 |
| `parallel_functions.py` | Function Calling 전체 흐름 - 함수 호출 → 로컬 실행 → 결과 재전달 → 최종 답변 생성 |

### 2. Semantic Kernel 입문

| 파일 | 설명 |
|------|------|
| `SK_connecting.py` | SK 커널 초기화 및 OpenAI 서비스 연결, `invoke_prompt`로 간단한 프롬프트 실행 |
| `SK_first_skill.py` | 프롬프트 템플릿 정의 (`InputVariable`), `PromptTemplateConfig`로 함수 생성 및 인자 바인딩 |

### 3. Semantic Plugin (디렉토리 기반)

| 파일 | 설명 |
|------|------|
| `SK_recommend_skill.py` | `plugins/Recommender` 디렉토리에서 Semantic Plugin 로드, 시청 영화 기반 추천 |
| `SK_context_variables.py` | `KernelPlugin.from_directory`로 플러그인 로드, `KernelArguments`를 통한 컨텍스트 변수 전달 |
| `SK_travel.py` | `plugins/TravelPlugin` 로드, 지역/예산/활동 기반 여행지 추천 |
| `SK_calc4.py` | `plugins/MathPlugin` 디렉토리 방식 로드, 파일 분리형 사칙연산 |

### 4. 인라인 프롬프트 함수 & 체이닝

| 파일 | 설명 |
|------|------|
| `SK_calc.py` | 인라인 `PromptTemplateConfig`으로 사칙연산 함수 정의, `InputVariable` 활용 |
| `SK_calc2.py` | 2단계 체이닝 - 자연어에서 인자 추출(JSON) → 실제 연산 수행 |
| `SK_calc3.py` | 의도 라우팅 - AI가 계산/일반 질문을 판단하여 분기 처리 (while 루프 대화) |

### 5. Native Function & 하이브리드

| 파일 | 설명 |
|------|------|
| `SK_native_functions.py` | `@kernel_function` 데코레이터로 Native Plugin 정의, 파일 I/O 후 Semantic 함수와 연동 |
| `SK_semantic_native_functions.py` | 프롬프트 내에서 `{{플러그인.함수}}` 구문으로 Native 함수를 자동 호출 |

### 6. 외부 API 연동 & 대화형 챗봇

| 파일 | 설명 |
|------|------|
| `SK_service_chat.py` | TMDb API 플러그인 + `ChatHistory` + 자동 함수 호출(`FunctionChoiceBehavior.Auto`)을 결합한 대화형 영화 챗봇 |
| `test_tmdb_service.py` | TMDb 플러그인 단독 테스트 - 장르 조회, 영화/TV 추천 기능 검증 |

## 플러그인 디렉토리 (`plugins/`)

| 플러그인 | 함수 | 설명 |
|----------|------|------|
| `FunPlugin` | Joke, Excuses, Limerick | 재미 요소 생성 (농담, 변명, 리머릭) |
| `MathPlugin` | Calculator | 사칙연산 수행 |
| `Recommender` | Recommend, Recommend_Movies | 주제/장르 기반 콘텐츠 추천, 시청 기록 기반 영화 추천 |
| `TravelPlugin` | SuggestDestination | 지역/예산/활동 기반 여행지 추천 |
| `Movies` | tmdb.py, tmdb_v2.py | TMDb API 연동 Native Plugin (장르 조회, 영화/TV 추천) |

## 콘솔 앱 (`SK_console_app/`)

`sk-python-hello-world/` - Semantic Kernel 공식 Hello World 샘플 프로젝트 (Poetry 기반)

## 학습 순서 (권장)

```
1. first_function.py          → OpenAI Function Calling 이해
2. parallel_functions.py       → 함수 실행 + 결과 재전달 흐름
3. SK_connecting.py            → SK 커널 기본 연결
4. SK_first_skill.py           → 프롬프트 템플릿 & 인자 바인딩
5. SK_recommend_skill.py       → 디렉토리 기반 Semantic Plugin
6. SK_calc.py → SK_calc2.py → SK_calc3.py → SK_calc4.py  → 프롬프트 함수 심화
7. SK_native_functions.py      → Native Function 정의
8. SK_semantic_native_functions.py → Semantic + Native 통합
9. SK_travel.py                → 플러그인 응용
10. SK_service_chat.py         → 대화형 에이전트 완성
```
