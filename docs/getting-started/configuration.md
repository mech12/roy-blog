---
layout: default
title: 설정 방법
parent: 시작하기
nav_order: 2
---

# 설정 방법

블로그 설정을 커스터마이징하는 방법입니다.

## _config.yml 주요 설정

```yaml
# 사이트 기본 정보
title: Roy's Tech Blog
description: 기술 문서화 블로그

# URL 설정
baseurl: "/roy-blog"
url: "https://mech12.github.io"

# 테마 설정
remote_theme: just-the-docs/just-the-docs
color_scheme: light
```

## 색상 테마 변경

`_config.yml`에서 `color_scheme` 값을 변경:

- `light` - 라이트 모드
- `dark` - 다크 모드

## 검색 기능

검색은 기본으로 활성화되어 있습니다. 상단 검색창을 통해 모든 문서를 검색할 수 있습니다.
