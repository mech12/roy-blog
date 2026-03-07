.PHONY: help install clean run

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

help:
	@echo "사용법:"
	@echo "  make install  - Python 가상환경 생성 및 패키지 설치"
	@echo "  make clean    - 가상환경 삭제"
	@echo "  make run F=<파일명>  - Python 스크립트 실행 (예: make run F=실습1일차/chapter_2/connecting.py)"

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
