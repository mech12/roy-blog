---
layout: default
title: 설치 가이드
parent: 시작하기
nav_order: 1
---

# 설치 가이드

개발 환경을 설정하는 방법을 설명합니다.

## 필수 요구사항

- Ruby 3.0 이상
- Git
- 텍스트 에디터 (VS Code 권장)

## 설치 단계

### 1. Ruby 설치 (macOS)

```bash
brew install ruby
```

### 2. Jekyll 설치

```bash
gem install jekyll bundler
```

### 3. 프로젝트 클론

```bash
git clone https://github.com/mech12/roy-blog.git
cd roy-blog
bundle install
```

## 로컬 서버 실행

```bash
make local
# 또는
bundle exec jekyll serve
```

브라우저에서 `http://localhost:4000/roy-blog/` 접속
