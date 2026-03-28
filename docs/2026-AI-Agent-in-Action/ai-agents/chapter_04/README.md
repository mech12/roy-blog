# Chapter 04 - 멀티 에이전트 프레임워크 예제

AutoGen과 CrewAI를 활용한 멀티 에이전트 협업 예제 모음입니다.

---

## 1. 사전 준비 요약

### 필요한 외부 서비스 (SaaS)

| 서비스 | 필수 여부 | 가입 URL | 필요한 키 | 사용하는 파일 |
|--------|-----------|----------|-----------|---------------|
| **OpenAI API** | 필수 | https://platform.openai.com | `OPENAI_API_KEY` | 전체 파일 |
| **AgentOps** | 선택 | https://app.agentops.ai | `AGENTOPS_API_KEY` | crewai_agentops.py, crewai_coding_crew.py, crewai_hierarchy.py |
| **Azure OpenAI** | 선택 | https://portal.azure.com | api_key, base_url | AutoGen 파일 (OAI_CONFIG_LIST에서 설정) |

> **AgentOps**는 에이전트 실행을 모니터링/추적하는 SaaS 서비스입니다.
> 무료 플랜이 있으며, API 키 없이 실행하면 경고만 출력되고 동작은 합니다.
> 필요 없다면 해당 파일에서 `agentops.init()` 줄을 주석 처리해도 됩니다.

---

## 2. 환경 설정

### 2-1. Python 패키지 설치

```bash
make install
```

또는 수동 설치:

```bash
pip install pyautogen crewai[tools] python-dotenv agentops langchain-openai requests pygame
```

### 2-2. AutoGen 설정 파일 (`OAI_CONFIG_LIST`)

AutoGen 예제 4개 파일이 이 파일을 읽습니다.

```bash
cp OAI_CONFIG_LIST.sample OAI_CONFIG_LIST
```

`OAI_CONFIG_LIST` 파일을 열고 주석(// 줄) 4줄을 제거한 뒤, API 키를 입력합니다:

```json
[
    {
        "model": "gpt-4.1",
        "api_key": "sk-여기에-OpenAI-API-키-입력",
        "tags": ["gpt-4", "tool"]
    }
]
```

> Azure OpenAI를 사용하려면 sample 파일의 두 번째/세 번째 항목도 설정하세요.

### 2-3. CrewAI 설정 파일 (`.env`)

CrewAI 예제 4개 + describe_image.py가 `.env`를 읽습니다.

```bash
# .env 파일 생성
cat <<'EOF' > .env
OPENAI_API_KEY=sk-여기에-OpenAI-API-키-입력
AGENTOPS_API_KEY=여기에-AgentOps-API-키-입력
OPEN_API_KEY=sk-여기에-OpenAI-API-키-입력
EOF
```

| 환경변수 | 용도 | 필수 여부 |
|----------|------|-----------|
| `OPENAI_API_KEY` | CrewAI가 LLM 호출에 사용 | 필수 (CrewAI 파일) |
| `AGENTOPS_API_KEY` | AgentOps 모니터링 대시보드 연동 | 선택 (없으면 경고만 출력) |
| `OPEN_API_KEY` | describe_image.py에서 OpenAI Vision API 호출 | 필수 (describe_image만) |

---

## 3. 파일별 상세 정보

### AutoGen 예제

| 파일 | 설명 | 설정 파일 | 외부 서비스 | 실행 모드 |
|------|------|-----------|-------------|-----------|
| `autogen_start.py` | 단일 에이전트가 스네이크 게임 코딩 | OAI_CONFIG_LIST | OpenAI API | 대화형 (사용자 입력 필요) |
| `autogen_coding_critic.py` | 엔지니어 + 리뷰어 2인 협업 | OAI_CONFIG_LIST | OpenAI API | 대화형 |
| `autogen_coding_critic_cache.py` | 위와 동일 + 디스크 캐시 적용 | OAI_CONFIG_LIST | OpenAI API | 대화형 |
| `autogen_coding_group.py` | 엔지니어 + 비평가 그룹채팅 | OAI_CONFIG_LIST | OpenAI API | 자동 (입력 불필요) |

- AutoGen은 `config_list_from_json(env_or_file="OAI_CONFIG_LIST")`로 설정을 로드합니다.
- 대화형 예제는 터미널에서 사용자 입력을 기다립니다 (빈 줄 입력 = 자동 응답, "exit" = 종료).
- `working/` 디렉토리에 에이전트가 생성한 코드가 저장됩니다.

### CrewAI 예제

| 파일 | 설명 | 설정 파일 | 외부 서비스 | 실행 모드 |
|------|------|-----------|-------------|-----------|
| `crewai_introduction.py` | 유머 연구원 + 작가 기본 예제 | .env | OpenAI API | 자동 |
| `crewai_agentops.py` | 위와 동일 + AgentOps 추적 | .env | OpenAI API, **AgentOps** | 자동 |
| `crewai_coding_crew.py` | 3인 게임 코딩 Crew (Sequential) | .env | OpenAI API, **AgentOps** | 대화형 (게임 설명 입력) |
| `crewai_hierarchy.py` | 3인 게임 코딩 Crew (Hierarchical) | .env | OpenAI API, **AgentOps** | 대화형 (게임 설명 입력) |

- CrewAI는 `load_dotenv()`로 `.env` 파일에서 환경변수를 로드합니다.
- `crewai_hierarchy.py`는 추가로 `langchain-openai` 패키지가 필요합니다 (매니저 LLM 용도).
- `the_best_joke.md` 파일이 출력물로 생성됩니다 (crewai_introduction, crewai_agentops).

### 기타

| 파일 | 설명 | 설정 파일 | 외부 서비스 | 실행 모드 |
|------|------|-----------|-------------|-----------|
| `describe_image.py` | GPT-4 Vision으로 이미지 설명 | .env 또는 환경변수 | OpenAI API | 함수 호출 |

- `OPEN_API_KEY` 환경변수로 OpenAI API 키를 읽습니다 (주의: `OPENAI_API_KEY`가 아님).
- 기본 이미지 경로는 `animals.png` (이 폴더에 포함되어 있음).

---

## 4. 실행 방법

```bash
# 도움말
make help

# 패키지 설치
make install

# AutoGen 예제
make run-autogen-start          # 기본 단일 에이전트
make run-autogen-critic         # 엔지니어 + 리뷰어
make run-autogen-critic-cache   # 엔지니어 + 리뷰어 + 캐시
make run-autogen-group          # 그룹채팅 (자동)

# CrewAI 예제
make run-crewai-intro           # 유머 Crew 기본
make run-crewai-agentops        # 유머 Crew + AgentOps
make run-crewai-coding          # 게임 코딩 Crew (Sequential)
make run-crewai-hierarchy       # 게임 코딩 Crew (Hierarchical)

# 기타
make run-describe-image         # GPT-4 Vision 이미지 설명
```

---

## 5. 비용 참고

모든 예제는 OpenAI API를 호출하므로 **API 사용량에 따라 비용이 발생**합니다.

- 멀티 에이전트 예제는 여러 번의 LLM 호출이 연쇄적으로 발생합니다.
- 특히 `autogen_coding_group.py`(max_round=20)와 CrewAI 예제는 토큰 소모가 클 수 있습니다.
- `autogen_coding_critic_cache.py`는 디스크 캐시를 사용하여 동일 요청의 반복 비용을 절감합니다.

---

## 6. 생성되는 파일/디렉토리

| 경로 | 설명 | 생성 주체 |
|------|------|-----------|
| `working/` | AutoGen 에이전트가 생성한 코드 저장 | AutoGen 예제 |
| `the_best_joke.md` | CrewAI 유머 작가의 출력물 | crewai_introduction, crewai_agentops |
| `.cache/` | AutoGen 디스크 캐시 | autogen_coding_critic_cache, autogen_coding_group |

---

## 7. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `FileNotFoundError: OAI_CONFIG_LIST` | 설정 파일 없음 | `cp OAI_CONFIG_LIST.sample OAI_CONFIG_LIST` 후 API 키 입력 |
| `AuthenticationError` | API 키가 잘못됨 | OAI_CONFIG_LIST 또는 .env의 키 확인 |
| `agentops` 관련 Warning | AGENTOPS_API_KEY 미설정 | .env에 키 추가하거나, 무시해도 실행에 문제 없음 |
| `ModuleNotFoundError: No module named 'crewai'` | 패키지 미설치 | `make install` 실행 |
| `KeyError: 'OPEN_API_KEY'` | describe_image용 키 미설정 | .env에 `OPEN_API_KEY=sk-...` 추가 |
