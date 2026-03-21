.DEFAULT_GOAL := help
.PHONY: help install autogen clean

VENV := .venv
PYTHON := $(VENV)/bin/python
UV := uv

help: ## 사용 가능한 명령어 목록 표시
	@echo "Chapter 04: 멀티 에이전트 프레임워크"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-10s %s\n", $$1, $$2}'

install: ## 가상환경 생성 및 의존성 설치 (uv)
	$(UV) venv $(VENV) --python 3.11
	$(UV) pip install -r requirements.txt --python $(VENV)/bin/python

autogen: ## AutoGen Studio 실행 (port 8081)
	$(VENV)/bin/autogenstudio ui --port 8081

clean: ## 가상환경 삭제
	rm -rf $(VENV)
