# Jekyll 기반 GitHub 블로그 로드맵

기술 문서화에 적합한 Jekyll 블로그를 만들기 위한 단계입니다.

## 1. 환경 준비

```bash
# Ruby 설치 확인
ruby -v

# Jekyll과 Bundler 설치
gem install jekyll bundler
```

## 2. 테마 선택 (기술 문서용 추천)

| 테마 | 특징 |
|------|------|
| **Just the Docs** | 문서화 특화, 검색 기능, 네비게이션 |
| **Minimal Mistakes** | 다목적, 커스터마이징 용이 |
| **Documentation Theme** | 기술 문서 전용 |
| **Chirpy** | 깔끔한 UI, 다크모드 지원 |

## 3. 프로젝트 설정

```bash
# 새 Jekyll 사이트 생성
jekyll new roy-blog --skip-bundle
cd roy-blog

# 또는 테마 기반으로 시작 (예: Just the Docs)
# Gemfile에 테마 추가 후 bundle install
```

## 4. GitHub Pages 배포

1. GitHub에 `username.github.io` 또는 원하는 repo 생성
2. `_config.yml`에 baseurl 설정
3. GitHub Actions 또는 직접 push로 배포

## 5. 콘텐츠 구성

```text
├── _posts/          # 블로그 포스트
├── docs/            # 문서 페이지
├── _config.yml      # 사이트 설정
└── assets/          # 이미지, CSS 등
```
