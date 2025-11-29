# Roy's Tech Blog

기술 문서화 블로그

## 블로그 주소

<https://mech12.github.io/roy-blog/>

## 배포

```bash
./deploy.sh "커밋 메시지"
```

## 로컬 개발

```bash
bundle install
bundle exec jekyll serve
# http://localhost:4000/roy-blog/
```

## 새 포스트 작성

`_posts/YYYY-MM-DD-제목.md` 형식으로 파일 생성

```markdown
---
layout: post
title: "포스트 제목"
date: 2025-11-29
---

내용...
```
