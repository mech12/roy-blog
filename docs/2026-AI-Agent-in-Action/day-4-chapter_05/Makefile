.PHONY: help install \
	first-function parallel-functions \
	sk-connecting sk-first-skill \
	sk-recommend sk-context-vars sk-travel sk-calc4 \
	sk-calc sk-calc2 sk-calc3 \
	sk-native sk-semantic-native \
	sk-service-chat test-tmdb

help: ## 사용 가능한 명령어 목록 출력
	@echo ""
	@echo "=== Chapter 05 - Semantic Kernel 실습 ==="
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ──────────────────────────────────────────────
# 환경 설정
# ──────────────────────────────────────────────

install: ## 실습에 필요한 모든 패키지 설치 (uv)
	uv pip install -r requirements.txt

# ──────────────────────────────────────────────
# 1. OpenAI Function Calling 기초
# ──────────────────────────────────────────────

first-function: ## [1] OpenAI Function Calling 기본 - 함수 설계도 정의 및 호출 판단
	uv run python first_function.py

parallel-functions: ## [1] Function Calling 전체 흐름 - 로컬 함수 실행 후 최종 답변 생성
	uv run python parallel_functions.py

# ──────────────────────────────────────────────
# 2. Semantic Kernel 입문
# ──────────────────────────────────────────────

sk-connecting: ## [2] SK 커널 초기화 및 OpenAI 연결, invoke_prompt 실행
	uv run python SK_connecting.py

sk-first-skill: ## [2] 프롬프트 템플릿 정의, InputVariable 및 인자 바인딩
	uv run python SK_first_skill.py

# ──────────────────────────────────────────────
# 3. Semantic Plugin (디렉토리 기반)
# ──────────────────────────────────────────────

sk-recommend: ## [3] plugins/Recommender 로드, 시청 영화 기반 추천
	uv run python SK_recommend_skill.py

sk-context-vars: ## [3] KernelPlugin.from_directory + KernelArguments 컨텍스트 변수
	uv run python SK_context_variables.py

sk-travel: ## [3] plugins/TravelPlugin - 지역/예산/활동 기반 여행지 추천
	uv run python SK_travel.py

sk-calc4: ## [3] plugins/MathPlugin 디렉토리 방식 로드, 파일 분리형 사칙연산
	uv run python SK_calc4.py

# ──────────────────────────────────────────────
# 4. 인라인 프롬프트 함수 & 체이닝
# ──────────────────────────────────────────────

sk-calc: ## [4] 인라인 PromptTemplateConfig 사칙연산 함수 정의
	uv run python SK_calc.py

sk-calc2: ## [4] 2단계 체이닝 - 자연어 인자 추출(JSON) → 연산 수행
	uv run python SK_calc2.py

sk-calc3: ## [4] 의도 라우팅 - 계산/일반 질문 분기 처리 (대화 루프)
	uv run python SK_calc3.py

# ──────────────────────────────────────────────
# 5. Native Function & 하이브리드
# ──────────────────────────────────────────────

sk-native: ## [5] @kernel_function Native Plugin 정의, 파일 I/O + Semantic 연동
	uv run python SK_native_functions.py

sk-semantic-native: ## [5] 프롬프트 내 {{플러그인.함수}} 구문으로 Native 자동 호출
	uv run python SK_semantic_native_functions.py

# ──────────────────────────────────────────────
# 6. 외부 API 연동 & 대화형 챗봇
# ──────────────────────────────────────────────

sk-service-chat: ## [6] TMDb + ChatHistory + 자동 함수 호출 대화형 영화 챗봇
	uv run python SK_service_chat.py

test-tmdb: ## [6] TMDb 플러그인 단독 테스트 - 장르 조회, 영화/TV 추천
	uv run python test_tmdb_service.py
