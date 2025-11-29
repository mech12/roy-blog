# Jekyll 기반 GitHub 블로그 설정 가이드

## 블로그 정보

- **URL**: https://mech12.github.io/roy-blog/
- **Repository**: https://github.com/mech12/roy-blog
- **테마**: Minimal (pages-themes/minimal)

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
│       └── jekyll.yml      # GitHub Actions 배포 워크플로우
├── _posts/                  # 블로그 포스트 (YYYY-MM-DD-title.md)
├── _config.yml              # Jekyll 설정
├── Gemfile                  # Ruby 의존성
├── index.markdown           # 메인 페이지
├── about.markdown           # About 페이지
├── 404.html                 # 404 페이지
└── deploy.sh                # 배포 스크립트
```

## 3. 주요 설정 파일

### _config.yml

```yaml
title: Roy's Tech Blog
description: 기술 문서화 블로그
baseurl: "/roy-blog"
url: "https://mech12.github.io"
repository: mech12/roy-blog

remote_theme: pages-themes/minimal@v0.2.0
plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-remote-theme
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
bundle install

# 로컬 서버 실행 (http://localhost:4000/roy-blog/)
bundle exec jekyll serve
```

## 6. 새 포스트 작성

`_posts/` 폴더에 `YYYY-MM-DD-제목.md` 형식으로 파일 생성:

```markdown
---
layout: post
title: "포스트 제목"
date: 2025-11-29
categories: [카테고리]
---

포스트 내용...
```

## 7. 배포

```bash
# 방법 1: deploy.sh 스크립트 사용
./deploy.sh "커밋 메시지"

# 방법 2: 수동 배포
git add .
git commit -m "커밋 메시지"
git push origin main
```

GitHub Actions가 자동으로 빌드 및 배포합니다.
