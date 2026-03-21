# Chapter 05: Function Calling과 Semantic Kernel

## 개요

이 챕터에서는 OpenAI의 Function Calling 기능과 Microsoft의 Semantic Kernel 프레임워크를 활용하여 AI 에이전트가 외부 함수를 호출하고, 플러그인 기반으로 기능을 확장하는 방법을 다룬다. 단순한 함수 정의부터 시작하여 병렬 함수 호출, Semantic Kernel의 커널 구성, 시맨틱/네이티브 함수 조합, 그리고 외부 API(TMDb)와의 연동까지 단계적으로 학습한다.

---

## 파일 설명

### OpenAI Function Calling 기초

| 파일 | 설명 |
|------|------|
| `first_function.py` | OpenAI Function Calling의 가장 기본적인 사용법을 보여준다. `recommend`라는 함수를 tools 파라미터로 정의하고, 사용자의 자연어 요청에서 topic과 rating을 자동으로 추출하는 과정을 시연한다. |
| `parallel_functions.py` | 하나의 사용자 요청에 대해 여러 함수 호출을 병렬로 처리하는 방법을 다룬다. 영화, 레시피, 선물 추천을 동시에 요청하면 모델이 각각에 대해 tool_call을 생성하고, 결과를 다시 모델에 전달하여 최종 응답을 구성한다. |

### Semantic Kernel 기초

| 파일 | 설명 |
|------|------|
| `SK_connecting.py` | Semantic Kernel 커널을 초기화하고 OpenAI 또는 Azure OpenAI 서비스에 연결하는 기본 구성 방법을 보여준다. `invoke_prompt`를 통해 간단한 프롬프트를 실행한다. |
| `SK_context_variables.py` | Semantic Kernel에서 컨텍스트 변수(InputVariable)를 사용하여 프롬프트 템플릿에 동적 값을 주입하는 방법을 다룬다. subject, format, genre, custom 등의 변수를 정의하고 `PromptTemplateConfig`로 구성한다. |
| `SK_first_skill.py` | 플러그인 디렉토리에서 시맨틱 함수를 불러와 실행하는 방법을 보여준다. `import_plugin_from_prompt_directory`를 사용하여 Recommender 플러그인의 Recommend_Movies 함수를 로드하고, 이미 본 영화 목록을 입력으로 전달한다. |
| `SK_recommend_skill.py` | Semantic Kernel의 이전 버전 API를 사용한 추천 스킬 구현 예제이다. `import_semantic_plugin_from_directory`와 `create_new_context`를 사용하여 컨텍스트 기반으로 영화를 추천한다. |

### Semantic Kernel 심화

| 파일 | 설명 |
|------|------|
| `SK_native_functions.py` | 네이티브 함수(Python 클래스 기반)를 Semantic Kernel에 등록하는 방법을 다룬다. `MySeenMoviesDatabase` 클래스에서 `@kernel_function` 데코레이터로 `seen_movies.txt` 파일을 읽는 함수를 정의하고, 이를 시맨틱 함수와 결합하여 추천에 활용한다. |
| `SK_semantic_native_functions.py` | 시맨틱 함수와 네이티브 함수를 하나의 프롬프트 안에서 결합하는 고급 패턴을 보여준다. 프롬프트 템플릿 내에서 `{{SeenMoviesPlugin.LoadSeenMovies}}`와 같은 표현식으로 네이티브 함수를 직접 호출한다. |
| `SK_service_chat.py` | Semantic Kernel 기반의 대화형 챗봇 구현 예제이다. ChatHistory를 활용한 대화 이력 관리, TMDb 서비스 플러그인 연동, 그리고 `chat_completion_with_tool_call`을 통한 자동 함수 호출을 포함한다. |

### 외부 서비스 연동

| 파일 | 설명 |
|------|------|
| `test_tmdb_service.py` | TMDb(The Movie Database) API 서비스 플러그인의 각 함수를 테스트하는 스크립트이다. 장르 ID 조회, 장르별 인기 영화/TV 프로그램 조회 등의 기능을 검증한다. |

### 데이터 및 설정 파일

| 파일 | 설명 |
|------|------|
| `requirements.txt` | 프로젝트 의존성 패키지 목록이다. openai, python-dotenv, semantic-kernel을 포함한다. |
| `seen_movies.txt` | 사용자가 이미 시청한 영화 목록 데이터이다. Matrix 시리즈 4편이 기록되어 있으며, 네이티브 함수에서 읽어와 추천 제외 목록으로 사용된다. |

### 디렉토리

| 디렉토리 | 설명 |
|-----------|------|
| `plugins/Recommender/` | 시맨틱 함수 플러그인이다. `Recommend`와 `Recommend_Movies` 두 가지 추천 함수가 각각 `skprompt.txt`(프롬프트 템플릿)와 `config.json`(설정)으로 구성되어 있다. |
| `plugins/Movies/` | TMDb API를 래핑한 네이티브 함수 플러그인이다. `tmdb.py`에서 영화/TV 장르 조회, 장르별 인기 콘텐츠 조회 등의 기능을 `@kernel_function` 데코레이터로 제공한다. |
| `SK_console_app/` | Semantic Kernel을 활용한 콘솔 애플리케이션 예제이다. `FunSkill` 플러그인(Joke, Excuses, Limerick)을 불러와 `ContextVariables`로 입력값을 전달하는 초기 버전의 Semantic Kernel 사용법을 보여준다. |

---

## 핵심 개념

### 1. OpenAI Function Calling
- **함수 스키마 정의**: JSON Schema 형식으로 함수의 이름, 설명, 매개변수를 정의하여 `tools` 파라미터로 전달한다.
- **자동 인자 추출**: 모델이 사용자의 자연어 입력에서 함수 매개변수 값을 자동으로 추출한다.
- **병렬 호출**: 하나의 요청에 대해 여러 함수를 동시에 호출하고, 각 결과를 수집하여 최종 응답을 생성한다.
- **도구 호출 루프**: 모델 응답에서 tool_calls를 확인하고, 함수를 실행한 뒤 결과를 다시 모델에 전달하는 순환 구조를 이해한다.

### 2. Semantic Kernel 아키텍처
- **커널(Kernel)**: AI 서비스와 플러그인을 관리하는 중앙 오케스트레이터이다.
- **시맨틱 함수**: `skprompt.txt`와 `config.json`으로 구성된 프롬프트 기반 함수이다. 디렉토리 구조로 관리된다.
- **네이티브 함수**: Python 클래스의 메서드에 `@kernel_function` 데코레이터를 적용하여 정의한다. 파일 읽기, API 호출 등 실제 코드 로직을 수행한다.
- **플러그인**: 시맨틱 함수와 네이티브 함수를 묶어 관리하는 단위이다.

### 3. 프롬프트 템플릿과 변수
- `{{$variable_name}}` 구문으로 동적 변수를 프롬프트에 삽입한다.
- `{{PluginName.FunctionName}}` 구문으로 프롬프트 내에서 다른 함수를 호출한다.
- `InputVariable`로 변수의 이름, 설명, 필수 여부를 정의한다.

### 4. 외부 API 통합 (TMDb)
- TMDb API를 Semantic Kernel의 네이티브 함수로 래핑하여 영화/TV 프로그램 데이터를 조회한다.
- 챗봇에서 자동으로 적절한 API 함수를 선택하여 호출하는 도구 호출 자동화를 구현한다.

---

## 학습 교훈

1. **Function Calling은 구조화된 출력의 핵심이다.** 자연어 입력을 정형화된 함수 호출로 변환하는 것이 AI 에이전트의 실용적 활용을 가능하게 한다. JSON Schema로 함수를 명확히 정의할수록 모델의 인자 추출 정확도가 높아진다.

2. **시맨틱 함수와 네이티브 함수의 분리가 중요하다.** 프롬프트 기반의 AI 로직(시맨틱 함수)과 코드 기반의 비즈니스 로직(네이티브 함수)을 분리하면 각각을 독립적으로 개선하고 테스트할 수 있다. `SK_semantic_native_functions.py`에서 보듯이 프롬프트 안에서 네이티브 함수를 직접 호출하는 패턴은 이 두 가지를 효과적으로 결합한다.

3. **플러그인 아키텍처는 재사용성과 확장성을 높인다.** TMDb 서비스를 플러그인으로 구성함으로써 여러 스크립트에서 동일한 기능을 재사용할 수 있다. 새로운 API 서비스를 추가할 때도 기존 코드를 수정하지 않고 새 플러그인만 등록하면 된다.

4. **대화 이력 관리는 챗봇 품질을 좌우한다.** `SK_service_chat.py`에서 보듯이 ChatHistory를 통해 시스템 메시지, 사용자 입력, 어시스턴트 응답을 체계적으로 관리하면 맥락을 유지하는 자연스러운 대화가 가능해진다.

5. **병렬 함수 호출은 효율성의 핵심이다.** `parallel_functions.py`에서 보듯이 여러 독립적인 작업을 하나의 요청으로 처리하면 응답 시간을 크게 줄일 수 있다. 모델이 여러 tool_call을 동시에 생성하고 결과를 종합하는 패턴을 이해하는 것이 중요하다.

6. **프레임워크 버전 변화에 주의해야 한다.** `SK_recommend_skill.py`(이전 API)와 `SK_first_skill.py`(현재 API)를 비교하면 Semantic Kernel의 API가 크게 변화했음을 알 수 있다. `import_semantic_plugin_from_directory`에서 `import_plugin_from_prompt_directory`로, `create_new_context`에서 `KernelArguments`로 전환되었으므로, 공식 문서와 버전을 항상 확인해야 한다.
