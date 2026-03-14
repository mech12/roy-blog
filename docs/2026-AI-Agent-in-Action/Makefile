.PHONY: help install clean run subtree-setup subtree-pull rebase push

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

# subtree 설정
REMOTE_AGENTS := wikibook-ai-agents
URL_AGENTS := https://github.com/wikibook/ai-agents.git
PREFIX_AGENTS := docs/2026-AI-Agent-in-Action/ai-agents
GIT_ROOT := $(shell git rev-parse --show-toplevel)
TARGET_BRANCH ?= main

help:
	@echo "사용법:"
	@echo "  make install  - Python 가상환경 생성 및 패키지 설치"
	@echo "  make clean    - 가상환경 삭제"
	@echo "  make run F=<파일명>  - Python 스크립트 실행 (예: make run F=실습1일차/chapter_2/connecting.py)"
	@echo ""
	@echo "subtree 관리:"
	@echo "  make rebase                              - 원본 저장소(main)에서 최신 내용 가져오기"
	@echo "  make rebase TARGET_BRANCH=dev            - 원본 저장소(dev)에서 최신 내용 가져오기"
	@echo "  make push                                - 원본 저장소 main 브랜치로 push"
	@echo "  make push TARGET_BRANCH=dev              - 원본 저장소 dev 브랜치로 push"
	@echo ""
	@echo "원본 저장소:"
	@echo "  ai-agents  $(URL_AGENTS)"

subtree-setup:
	@cd $(GIT_ROOT) && (git remote get-url $(REMOTE_AGENTS) >/dev/null 2>&1 || git remote add $(REMOTE_AGENTS) $(URL_AGENTS))
	@echo "remote ready"

subtree-pull: subtree-setup
	cd $(GIT_ROOT) && git subtree pull --prefix=$(PREFIX_AGENTS) $(REMOTE_AGENTS) $(TARGET_BRANCH) --squash

rebase: subtree-pull

push: subtree-setup
	cd $(GIT_ROOT) && git subtree push --prefix=$(PREFIX_AGENTS) $(REMOTE_AGENTS) $(TARGET_BRANCH)

install:
	@echo "📦 Python 가상환경 생성 중..."
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@echo "📦 패키지 설치 중..."
	$(PIP) install --upgrade pip -q
	$(PIP) install openai python-dotenv opencv-python pandas requests uvicorn fastapi watchdog -q
	@echo "✅ 설치 완료! 실행: make run F=실습1일차/chapter_2/connecting.py"

clean:
	@echo "🧹 가상환경 삭제 중..."
	rm -rf $(VENV_DIR)
	@echo "✅ 완료"

run:
	@test -n "$(F)" || (echo "❌ 파일을 지정하세요: make run F=파일경로.py" && exit 1)
	$(PYTHON) $(F)
