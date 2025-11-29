.PHONY: help local prod install clean kill

help:
	@echo "사용법:"
	@echo "  make local    - 로컬 서버 실행"
	@echo "  make prod     - GitHub Pages 배포"
	@echo "  make install  - 의존성 설치"
	@echo "  make clean    - 빌드 캐시 삭제"

install:
	@echo "📦 의존성 설치 중..."
	bundle install

local:
	@echo "🚀 로컬 서버 시작..."
	@echo ""
	@echo "🔗 로컬 주소: http://localhost:4000/roy-blog/"
	@echo ""
	bundle exec jekyll serve

prod:
	@./deploy.sh "$(msg)"

clean:
	@echo "🧹 캐시 삭제 중..."
	rm -rf _site .jekyll-cache .sass-cache
	@echo "✅ 완료"

kill:
	@echo "🔪 포트 4000 프로세스 종료 중..."
	@lsof -ti:4000 | xargs kill -9 2>/dev/null || echo "포트 4000에 실행 중인 프로세스가 없습니다."
	@echo "✅ 완료"
