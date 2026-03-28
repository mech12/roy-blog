.PHONY: help local prod install clean kill git-sync git-rebase git-merge git-reset git-branch-new git-branch-rename git-help

help:
	@echo "사용법:"
	@echo "  make local             - 로컬 서버 실행"
	@echo "  make prod              - GitHub Pages 배포"
	@echo "  make install           - 의존성 설치"
	@echo "  make clean             - 빌드 캐시 삭제"
	@echo "  make git-help          - Git 브랜치 관리 도움말"

install:
	@echo "📦 시스템 의존성 설치 중..."
	@which ruby > /dev/null 2>&1 || (echo "🔧 Ruby 설치 중..." && sudo apt-get update && sudo apt-get install -y ruby-full build-essential)
	@which bundle > /dev/null 2>&1 || (echo "🔧 Bundler 설치 중..." && sudo gem install bundler)
	@echo "📦 Ruby 의존성 설치 중..."
	bundle config set --local path 'vendor/bundle'
	bundle install

local:
	@echo "🚀 로컬 서버 시작..."
	@echo ""
	@echo "🔗 로컬 주소: http://localhost:4000/roy-blog/"
	@echo ""
	bundle exec jekyll serve --livereload --host 0.0.0.0

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

# ##########################################
# Git 브랜치 관리
# ##########################################

git-sync: # 현재 브랜치를 origin과 동기화 (커밋→rebase→push)
	@CB=$$(git branch --show-current); \
	if [ "$$CB" = "main" ]; then \
		echo "❌ Error: main 브랜치에서는 실행할 수 없습니다."; exit 1; \
	fi; \
	echo "=== 동기화 대상: origin/$$CB ==="; \
	echo ""; \
	if [ -n "$$(git status --porcelain)" ]; then \
		echo "=== 수정사항 발견 - 자동 커밋 중... ==="; \
		git add -A && git commit -m "chore: 임시커밋"; \
		echo ""; \
	fi; \
	echo "=== 원격 브랜치 fetch 중: origin/$$CB ==="; \
	git fetch origin $$CB && \
	echo "" && \
	echo "=== rebase 중: origin/$$CB ===" && \
	git rebase origin/$$CB && \
	echo "" && \
	echo "=== 원격에 push 중: HEAD → origin/$$CB ===" && \
	git push --force-with-lease origin HEAD:$$CB && \
	echo "" && \
	echo "=== 동기화 완료 ==="

git-rebase: # 현재 브랜치를 TARGET 기준으로 rebase [TARGET=기준브랜치, 기본값 main]
	@CB=$$(git branch --show-current); \
	TG="$(TARGET)"; if [ -z "$$TG" ]; then TG="main"; fi; \
	if [ "$$CB" = "$$TG" ]; then \
		echo "❌ Error: 현재 $$TG 브랜치에서는 실행할 수 없습니다."; exit 1; \
	fi; \
	echo ""; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo "  $$CB → origin/$$TG rebase"; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo ""; \
	echo "=== [1/3] origin/$$TG fetch ===" && \
	git fetch origin $$TG && \
	echo "=== [2/3] origin/$$TG 기준으로 rebase ===" && \
	if ! git rebase origin/$$TG; then \
		echo ""; \
		echo "  ❌ rebase 충돌! 자동으로 abort합니다."; \
		git diff --name-only --diff-filter=U 2>/dev/null | while read f; do echo "  충돌 파일: $$f"; done; \
		git rebase --abort; \
		echo "  수동으로 해결하려면: git rebase origin/$$TG"; \
		exit 1; \
	fi && \
	echo "=== [3/3] 원격에 push ===" && \
	git push --force-with-lease origin $$CB && \
	echo "" && \
	echo "✅ rebase 완료!"

git-merge: # 현재 브랜치를 TARGET에 merge [TARGET=대상브랜치, 기본값 main]
	@CB=$$(git branch --show-current); \
	TG="$(TARGET)"; if [ -z "$$TG" ]; then TG="main"; fi; \
	if [ "$$CB" = "$$TG" ]; then \
		echo "❌ Error: 현재 $$TG 브랜치에서는 실행할 수 없습니다."; exit 1; \
	fi; \
	echo ""; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo "  $$CB 브랜치를 $$TG에 merge합니다."; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo ""; \
	echo "=== [1/5] $$TG 브랜치로 전환 ===" && \
	git checkout $$TG && \
	echo "=== [2/5] $$TG 최신 pull ===" && \
	git pull origin $$TG && \
	echo "=== [3/5] $$CB 브랜치 merge ===" && \
	if ! git merge $$CB; then \
		echo ""; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		echo "  ❌ merge 충돌 발생! 자동으로 abort합니다."; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		git diff --name-only --diff-filter=U 2>/dev/null | while read f; do echo "  충돌 파일: $$f"; done; \
		git merge --abort; \
		git checkout $$CB; \
		echo ""; \
		echo "  $$CB 브랜치로 복귀 완료."; \
		echo "  수동으로 해결하려면: git checkout $$TG && git merge $$CB"; \
		echo ""; \
		exit 1; \
	fi && \
	echo "=== [4/5] 원격에 push ===" && \
	git push origin $$TG && \
	echo "=== [5/5] $$CB 브랜치로 복귀 ===" && \
	git checkout $$CB && \
	echo "" && \
	echo "✅ $$CB → $$TG merge 완료! (현재 브랜치: $$CB)"

git-reset: # 현재 브랜치를 TARGET 최신 상태로 초기화 [TARGET=기준브랜치, 기본값 main]
	@CB=$$(git branch --show-current); \
	TG="$(TARGET)"; if [ -z "$$TG" ]; then TG="main"; fi; \
	if [ "$$CB" = "$$TG" ]; then \
		echo "❌ Error: 현재 $$TG 브랜치에서는 실행할 수 없습니다."; exit 1; \
	fi; \
	echo ""; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo "  $$CB 브랜치를 $$TG 최신 상태로 초기화합니다."; \
	echo "  (로컬 + 원격 모두 삭제 후 재생성)"; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo ""; \
	read -p "계속하시겠습니까? (y/N): " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "취소되었습니다."; \
		exit 0; \
	fi; \
	echo ""; \
	echo "=== [1/6] $$TG 브랜치로 전환 ===" && \
	git checkout $$TG && \
	echo "=== [2/6] $$TG 최신 pull ===" && \
	git pull origin $$TG && \
	echo "=== [3/6] 로컬 $$CB 브랜치 삭제 ===" && \
	(git branch -D $$CB 2>/dev/null || echo "  (로컬 브랜치 없음, 스킵)") && \
	echo "=== [4/6] 원격 $$CB 브랜치 삭제 ===" && \
	(git push origin --delete $$CB 2>/dev/null || echo "  (원격 브랜치 없음, 스킵)") && \
	echo "=== [5/6] 새 $$CB 브랜치 생성 ===" && \
	git checkout -b $$CB && \
	echo "=== [6/6] 원격에 push ===" && \
	git push --set-upstream origin $$CB && \
	echo "" && \
	echo "✅ $$CB 브랜치가 $$TG 최신 상태로 초기화되었습니다!"

git-branch-new: # 새 브랜치 생성 및 원격 push (예: make git-branch-new NEW_BRANCH=feat/xxx)
	@if [ -z "$(NEW_BRANCH)" ]; then \
		echo "사용법: make git-branch-new NEW_BRANCH=<브랜치명>"; \
		echo "예시: make git-branch-new NEW_BRANCH=feat/new-post"; \
		exit 1; \
	fi
	@echo "=== 새 브랜치 생성: $(NEW_BRANCH) ===" && \
	git checkout -b $(NEW_BRANCH) && \
	echo "=== 원격에 push: $(NEW_BRANCH) ===" && \
	git push -u origin $(NEW_BRANCH) && \
	echo "" && \
	echo "✅ $(NEW_BRANCH) 브랜치 생성 및 원격 push 완료!"

git-branch-rename: # 현재 브랜치 이름 변경 및 원격 적용 (예: make git-branch-rename NEW_BRANCH=feat/new-name)
	@if [ -z "$(NEW_BRANCH)" ]; then \
		echo "사용법: make git-branch-rename NEW_BRANCH=<새로운브랜치명>"; \
		echo ""; \
		echo "현재 브랜치: $$(git branch --show-current)"; \
		exit 1; \
	fi
	@OLD_BRANCH=$$(git branch --show-current); \
	echo "=== 브랜치 이름 변경: $$OLD_BRANCH → $(NEW_BRANCH) ==="; \
	git branch -m "$(NEW_BRANCH)" && \
	git push origin -u "$(NEW_BRANCH)" && \
	git push origin --delete "$$OLD_BRANCH" && \
	echo "" && \
	echo "✅ $$OLD_BRANCH → $(NEW_BRANCH) 브랜치 이름 변경 완료!"

git-help: ## Git 브랜치 관리 도움말 (make git-help)
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Git 명령어 목록"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  \033[36mgit-sync\033[0m              현재 브랜치를 origin과 동기화 (커밋→rebase→push)"
	@echo "  \033[36mgit-rebase\033[0m            현재 브랜치를 TARGET 기준으로 rebase [TARGET=기준브랜치, 기본값 main]"
	@echo "  \033[36mgit-merge\033[0m             현재 브랜치를 TARGET에 merge [TARGET=대상브랜치, 기본값 main]"
	@echo "  \033[36mgit-reset\033[0m             현재 브랜치를 TARGET 최신 상태로 초기화 [TARGET=기준브랜치, 기본값 main]"
	@echo "  \033[36mgit-branch-new\033[0m        새 브랜치 생성 및 원격 push (예: make git-branch-new NEW_BRANCH=feat/xxx)"
	@echo "  \033[36mgit-branch-rename\033[0m     현재 브랜치 이름 변경 및 원격 적용 (예: make git-branch-rename NEW_BRANCH=feat/new-name)"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Git 브랜치 관리 참고 명령어"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "▶ 브랜치를 origin/main 최신 상태로 초기화 (예: feat/post)  → make git-reset"
	@echo "  git checkout main"
	@echo "  git pull origin main"
	@echo "  git branch -d feat/post"
	@echo "  git push origin --delete feat/post"
	@echo "  git checkout -b feat/post"
	@echo "  git push --set-upstream origin feat/post"
	@echo ""
	@echo "▶ 현재 브랜치와 origin/main 차이 확인"
	@echo "  git fetch origin main"
	@echo "  git log --oneline origin/main..HEAD   # 로컬에만 있는 커밋"
	@echo "  git log --oneline HEAD..origin/main   # origin/main에만 있는 커밋"
	@echo "  git diff HEAD origin/main --stat      # 파일 변경 요약"
	@echo ""
	@echo "▶ 작업 브랜치를 main 기준으로 rebase    → make git-rebase"
	@echo "  git fetch origin main"
	@echo "  git rebase origin/main"
	@echo "  git push --force-with-lease origin <branch>"
	@echo ""
	@echo "▶ 작업 브랜치를 main에 merge             → make git-merge"
	@echo "  git checkout main"
	@echo "  git pull origin main"
	@echo "  git merge <branch>"
	@echo "  git push origin main"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  rebase vs merge 차이"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "▶ rebase (make git-rebase) — 히스토리를 일렬로 정리"
	@echo "  변경 전:                    변경 후:"
	@echo "  A---B---C---D  (main)      A---B---C---D  (main)"
	@echo "       \\                                  \\"
	@echo "        E---F  (feat)                      E'---F'  (feat)"
	@echo ""
	@echo "▶ merge (make git-merge) — 합류 지점 생성"
	@echo "  변경 전:                    변경 후:"
	@echo "  A---B---C---D  (main)      A---B---C---D---M  (main)"
	@echo "       \\                          \\         /"
	@echo "        E---F  (feat)              E---F  (feat)"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Makefile 내장 Git 명령어 (항상 현재 브랜치 기준, TARGET 기본값: main)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  make git-sync                        # 현재 브랜치 ↔ origin 동기화 (커밋→rebase→push)"
	@echo "  make git-rebase                      # 현재 브랜치를 main 기준으로 rebase"
	@echo "  make git-rebase TARGET=develop        # 현재 브랜치를 develop 기준으로 rebase"
	@echo "  make git-merge                       # 현재 브랜치를 main에 merge"
	@echo "  make git-reset                       # 현재 브랜치를 main 최신으로 초기화"
	@echo "  make git-branch-new NEW_BRANCH=x     # 새 브랜치 생성 및 원격 push"
	@echo "  make git-branch-rename NEW_BRANCH=x  # 브랜치 이름 변경"
	@echo ""
	@echo "  일반적인 작업 흐름:"
	@echo "  1. 작업 브랜치에서 작업 & 커밋"
	@echo "  2. make git-sync       ← 내 작업을 origin에 push"
	@echo "  3. make git-rebase     ← main에 새 커밋이 있으면 내 브랜치에 반영"
	@echo "  4. make git-merge      ← 작업 완료 후 main에 합치기"
	@echo ""
	@echo "  한번에 rebase → merge → reset:"
	@echo "  make git-rebase && make git-merge && make git-reset"
	@echo ""
