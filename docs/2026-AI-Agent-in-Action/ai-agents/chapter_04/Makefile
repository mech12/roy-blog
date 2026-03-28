.PHONY: help install \
	run-autogen-start run-autogen-critic run-autogen-critic-cache run-autogen-group \
	run-crewai-intro run-crewai-agentops run-crewai-coding run-crewai-hierarchy \
	run-describe-image

help: ## 사용 가능한 명령어 목록
	@echo "=============================================="
	@echo " Chapter 04 - 멀티 에이전트 예제"
	@echo "=============================================="
	@echo ""
	@echo "  make install                  : 필요한 패키지 설치"
	@echo ""
	@echo "  [AutoGen 예제]"
	@echo "  make run-autogen-start        : AutoGen 기본 예제 (대화형)"
	@echo "  make run-autogen-critic       : AutoGen 코딩+리뷰 예제 (대화형)"
	@echo "  make run-autogen-critic-cache : AutoGen 코딩+리뷰+캐시 예제 (대화형)"
	@echo "  make run-autogen-group        : AutoGen 그룹채팅 예제 (자동)"
	@echo ""
	@echo "  [CrewAI 예제]"
	@echo "  make run-crewai-intro         : CrewAI 기본 유머 예제"
	@echo "  make run-crewai-agentops      : CrewAI + AgentOps 유머 예제"
	@echo "  make run-crewai-coding        : CrewAI 게임 코딩 Crew (대화형)"
	@echo "  make run-crewai-hierarchy     : CrewAI 계층형 게임 Crew (대화형)"
	@echo ""
	@echo "  [기타]"
	@echo "  make run-describe-image       : GPT-4 Vision 이미지 설명"
	@echo ""
	@echo "  [사전 준비]"
	@echo "  - AutoGen 예제: OAI_CONFIG_LIST 파일 필요 (OAI_CONFIG_LIST.sample 참고)"
	@echo "  - CrewAI 예제: .env 파일에 OPENAI_API_KEY 설정 필요"
	@echo "  - describe_image: .env 파일에 OPEN_API_KEY 설정 필요"

# ──────────────────────────────────────────────
# 설치
# ──────────────────────────────────────────────
install: ## 필요한 Python 패키지 설치
	pip install pyautogen crewai[tools] python-dotenv agentops langchain-openai requests pygame

# ──────────────────────────────────────────────
# AutoGen 예제
# ──────────────────────────────────────────────
run-autogen-start: ## AutoGen 기본 예제 - 단일 에이전트 코딩 (대화형)
	python autogen_start.py

run-autogen-critic: ## AutoGen 코딩 + 리뷰어 예제 (대화형)
	python autogen_coding_critic.py

run-autogen-critic-cache: ## AutoGen 코딩 + 리뷰어 + 디스크 캐시 예제 (대화형)
	python autogen_coding_critic_cache.py

run-autogen-group: ## AutoGen 그룹채팅 (엔지니어+비평가) 예제 (자동 실행)
	python autogen_coding_group.py

# ──────────────────────────────────────────────
# CrewAI 예제
# ──────────────────────────────────────────────
run-crewai-intro: ## CrewAI 기본 유머 연구+작성 예제
	python crewai_introduction.py

run-crewai-agentops: ## CrewAI + AgentOps 유머 예제
	python crewai_agentops.py

run-crewai-coding: ## CrewAI 게임 코딩 Crew - Sequential (대화형 입력)
	python crewai_coding_crew.py

run-crewai-hierarchy: ## CrewAI 계층형 게임 Crew - Hierarchical (대화형 입력)
	python crewai_hierarchy.py

# ──────────────────────────────────────────────
# 기타
# ──────────────────────────────────────────────
run-describe-image: ## GPT-4 Vision으로 animals.png 이미지 설명
	python -c "from describe_image import describe_image; print(describe_image())"
