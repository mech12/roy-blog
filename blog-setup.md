# Jekyll 기반 GitHub 블로그 프로젝트 설정 가이드

## 블로그 정보

- **URL**: <https://mech12.github.io/roy-blog/>
- **Repository**: <https://github.com/mech12/roy-blog>
- **테마**: Just the Docs (문서화 특화, 왼쪽 트리 네비게이션)

## 1. 환경 준비

### macOS (Homebrew 사용)

```bash
# Homebrew Ruby 설치 (시스템 Ruby 권한 문제 해결)
brew install ruby

# PATH 설정 (~/.zshrc에 추가)
export PATH="/opt/homebrew/opt/ruby/bin:/opt/homebrew/lib/ruby/gems/3.4.0/bin:$PATH"

# Jekyll과 Bundler 설치
gem install jekyll bundler
```

## 2. 프로젝트 구조

```text
roy-blog/
├── .github/
│   └── workflows/
│       └── jekyll.yml       # GitHub Actions 배포 워크플로우
├── docs/                     # 문서 페이지 (네비게이션에 표시)
│   ├── getting-started/      # 시작하기 카테고리
│   ├── tutorials/            # 튜토리얼 카테고리
│   └── notes/                # 개발 노트 카테고리
├── _config.yml               # Jekyll 설정
├── Gemfile                   # Ruby 의존성
├── index.markdown            # 메인 페이지
├── Makefile                  # 빌드/배포 명령어
├── deploy.sh                 # 배포 스크립트
└── README.md                 # 블로그 사용 가이드
```

## 3. 주요 설정 파일

### _config.yml

```yaml
title: Roy's Tech Blog
description: 기술 문서화 블로그
baseurl: "/roy-blog"
url: "https://mech12.github.io"
repository: mech12/roy-blog

# Just the Docs 테마
remote_theme: just-the-docs/just-the-docs@v0.10.0
plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-remote-theme

# 검색 활성화
search_enabled: true

# 네비게이션 설정
nav_sort: case_insensitive
```

### Gemfile

```ruby
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "webrick"
```

## 4. 배포 방식

GitHub Actions를 통한 자동 배포:

- `main` 브랜치에 push하면 자동으로 빌드 및 배포
- 워크플로우: `.github/workflows/jekyll.yml`

## 5. 로컬 개발

```bash
# 의존성 설치
make install
# 또는: bundle install

# 로컬 서버 실행
make local
# 또는: bundle exec jekyll serve

# 접속: http://localhost:4000/roy-blog/
```

## 6. 배포

```bash
# Makefile 사용
make prod msg="커밋 메시지"

# 또는 deploy.sh 직접 사용
./deploy.sh "커밋 메시지"

# 또는 수동 배포
git add .
git commit -m "커밋 메시지"
git push origin main
```

GitHub Actions가 자동으로 빌드 및 배포합니다.
