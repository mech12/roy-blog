# Chapter 3 - GPT 어시스턴트 빌더와 커스텀 액션

OpenAI의 GPT 빌더(Custom GPTs)를 활용하여 다양한 목적의 AI 어시스턴트를 설계하고, FastAPI 기반 커스텀 액션(Custom Actions)을 통해 외부 API와 연동하는 방법을 실습하는 챕터입니다.

## 환경 설정

```bash
pip install -r requirements.txt
```

주요 의존성: `openai`, `fastapi`, `uvicorn`, `pandas`, `requests`, `beautifulsoup4`(웹 스크래핑용)

## 파일 목록

### GPT 어시스턴트 설계 (Instructions 파일)

| 파일 | 용도 | 설명 |
|------|------|------|
| `assistants_builder.txt` | FastAPI 서비스 생성 어시스턴트 | FastAPI 기반 API 서비스를 생성하고 OpenAPI 스펙을 자동으로 만들어주는 어시스턴트의 지침. 엔드포인트 정의부터 Pydantic 모델 설계, Ngrok 배포까지 전체 워크플로우를 안내한다. |
| `classic_robot_reads_v1.txt` | 독서 어시스턴트 (Isaac Asimov 페르소나) | 아이작 아시모프의 페르소나를 채택하여 지식 베이스에 업로드된 도서에 대해서만 논의하는 어시스턴트. 항상 3개의 예시를 제공하고 추가 요청을 확인하는 규칙을 따른다. |
| `culinary_companion_v1.txt` | 요리 어시스턴트 (Julia Child 페르소나) | 줄리아 차일드 스타일로 요리 조언을 제공하는 어시스턴트. 레시피 생성 시 완성 이미지, 칼로리/영양 정보, 쇼핑 목록 및 1인분 예상 비용을 함께 제공한다. |
| `data_scout_v1.txt` | 데이터 분석 어시스턴트 (Nate Silver 페르소나) | Nate Silver 스타일로 CSV 데이터를 분석하는 어시스턴트. 데이터 수집, EDA, 가설 검정, 예측 모델링, 인사이트 도출, 프레젠테이션까지 6단계 분석 파이프라인을 수행한다. |
| `task_organizer_v1.txt` | 업무 정리 어시스턴트 (Tim Ferriss 페르소나) | Tim Ferriss의 생산성 철학을 적용하여 일일 업무를 긴급도와 가용 시간 기준으로 우선순위를 정하고, 완료 시 시각화 차트를 생성하는 어시스턴트. |
| `task_organizer_assistant.txt` | 업무 정리 어시스턴트 (Assistants API 버전) | `task_organizer_v1.txt`와 동일한 기능이지만 Assistants API에서 사용하기 위한 지침 파일. |
| `custom_action_assistant_v1.txt` | 커스텀 액션 어시스턴트 | `assistants_builder.txt`와 동일한 내용으로, GPT가 외부 FastAPI 서비스를 호출하는 커스텀 액션을 구성하는 방법을 안내하는 지침. |

### Python 코드 파일

| 파일 | 용도 | 설명 |
|------|------|------|
| `daily_tasks_api.py` | 일일 업무 API 서버 | FastAPI로 구현한 간단한 REST API. Task 모델(id, description, completed)을 정의하고 `/tasks` GET 엔드포인트로 업무 목록을 반환한다. GPT 커스텀 액션의 백엔드로 사용된다. |
| `data_processor.py` | 데이터 처리 스크립트 | pandas를 사용하여 CSV 파일(`netflix_titles.csv`)을 로드하고 미리보기하는 기본 데이터 처리 코드. Data Scout 어시스턴트의 참고 예제이다. |
| `download_books.py` | 도서 다운로드 (AutoGen 생성) | AutoGen이 생성한 코드로, Project Gutenberg에서 로봇 관련 도서를 검색하고 텍스트 파일로 다운로드한다. BeautifulSoup을 활용한 웹 스크래핑 예제이다. |
| `download_texts.py` | 도서 다운로드 (개선 버전) | `download_books.py`의 개선 버전. 책 제목을 파일명으로 사용하고 파일명을 정제(sanitize)하는 기능이 추가되었다. Classic Robot Reads 어시스턴트의 지식 베이스 구축에 사용된다. |

### 설정 파일

| 파일 | 용도 | 설명 |
|------|------|------|
| `requirements.txt` | 의존성 목록 | openai, fastapi, uvicorn, pandas, requests 등 챕터 실습에 필요한 Python 패키지 목록. |

## 핵심 개념

### 1. GPT 빌더를 통한 커스텀 어시스턴트 설계

각 `.txt` 파일은 GPT 빌더의 Instructions(지침)으로 사용되며, 다음 요소를 포함한다:
- **페르소나 설정**: 유명 인물의 스타일을 채택하여 응답 톤과 전문성을 조절
- **행동 규칙(RULES)**: 어시스턴트가 반드시 따라야 할 구체적 행동 지침
- **작업 파이프라인**: 단계별 작업 흐름을 명시하여 일관된 결과 보장

### 2. 커스텀 액션 (Custom Actions)

GPT가 외부 API를 호출할 수 있도록 하는 메커니즘:
- `daily_tasks_api.py`가 FastAPI 백엔드 역할을 수행
- FastAPI가 자동 생성하는 OpenAPI 스펙을 GPT에 등록
- Ngrok을 통해 로컬 서버를 외부에 노출하여 GPT에서 접근 가능하게 구성

### 3. 지식 베이스 구축

`download_books.py`와 `download_texts.py`는 Project Gutenberg에서 도서를 자동 수집하여 GPT의 지식 베이스(Knowledge Base)로 업로드할 파일을 준비한다. 이를 통해 GPT가 특정 도메인의 텍스트만 참조하도록 제한할 수 있다.

### 4. 다양한 어시스턴트 패턴

이 챕터에서 다루는 어시스턴트는 각각 다른 GPT 기능을 활용한다:

| 어시스턴트 | 활용 기능 |
|-----------|----------|
| Classic Robot Reads | Knowledge Base (파일 업로드) |
| Culinary Companion | DALL-E (이미지 생성), 데이터 분석 |
| Data Scout | Code Interpreter (pandas, matplotlib, scikit-learn) |
| Task Organizer | Code Interpreter (시각화 차트 생성) |
| Custom Action Assistant | Custom Actions (외부 API 호출) |

## 학습 교훈

### 1. 좋은 어시스턴트 지침은 구체적이고 구조화되어야 한다

`data_scout_v1.txt`와 `classic_robot_reads_v1.txt`를 비교하면, 전자는 6단계의 명확한 파이프라인을 정의하고 각 단계에 구체적인 라이브러리와 함수명까지 명시한 반면, 후자는 간결한 규칙 기반으로 설계되었다. 두 접근 모두 유효하지만, 복잡한 작업일수록 단계별 지침이 더 안정적인 결과를 만든다.

### 2. 페르소나는 단순한 재미가 아니라 출력 품질을 결정한다

모든 어시스턴트가 실존 인물의 페르소나를 채택하고 있다. 이는 Chapter 2에서 배운 프롬프트 엔지니어링의 "페르소나 부여" 전략의 실전 적용이다. Nate Silver 페르소나는 데이터 분석의 엄밀함을, Tim Ferriss 페르소나는 효율 중심의 우선순위 결정을 자연스럽게 유도한다.

### 3. 커스텀 액션은 GPT의 한계를 실시간 데이터로 확장한다

GPT는 기본적으로 학습 데이터 이후의 정보를 알 수 없지만, `daily_tasks_api.py`와 같은 외부 API를 커스텀 액션으로 연결하면 실시간 데이터에 접근할 수 있다. 이때 FastAPI + OpenAPI 스펙 조합은 API 문서를 자동 생성해주므로 GPT와의 연동이 매우 간편하다.

### 4. 지식 베이스와 규칙의 조합이 환각(Hallucination)을 줄인다

`classic_robot_reads_v1.txt`에서 "지식 베이스 내의 텍스트만 참조하라"는 규칙은 GPT의 환각 문제를 제어하는 핵심 전략이다. 도메인을 제한하고 참조 범위를 명시적으로 한정함으로써, 어시스턴트가 존재하지 않는 정보를 생성하는 것을 방지한다.

### 5. AutoGen으로 생성한 코드도 수정이 필요하다

`download_books.py`(AutoGen 생성)와 `download_texts.py`(개선 버전)를 비교하면, AI가 생성한 코드를 그대로 사용하기보다 실제 환경에 맞게 수정하는 과정이 필요하다는 것을 알 수 있다. 파일명 정제, 에러 처리, 코드 구조 개선 등이 이에 해당한다.
