# Roy's Tech Blog

기술 문서화 블로그

## 블로그 주소

<https://mech12.github.io/roy-blog/>

## 네비게이션 구조

```text
├── Home
├── 시작하기
│   ├── 설치 가이드
│   └── 설정 방법
├── 튜토리얼
│   └── Jekyll 기초
└── 개발 노트
    └── 샘플 노트
```

---

## 블로그 글 작성 방법

### 1. 새 카테고리 추가

`docs/` 폴더 아래에 새 폴더를 만들고 `index.md` 생성:

```bash
mkdir docs/new-category
```

```markdown
<!-- docs/new-category/index.md -->
---
layout: default
title: 새 카테고리
nav_order: 5
has_children: true
permalink: /docs/new-category/
---

# 새 카테고리

카테고리 설명...
```

### 2. 새 페이지 추가

카테고리 폴더 안에 `.md` 파일 생성:

```markdown
<!-- docs/new-category/my-page.md -->
---
layout: default
title: 페이지 제목
parent: 새 카테고리
nav_order: 1
---

# 페이지 제목

내용 작성...
```

### 3. Front Matter 속성

| 속성 | 설명 | 예시 |
|------|------|------|
| `layout` | 레이아웃 (항상 `default`) | `default` |
| `title` | 네비게이션에 표시될 제목 | `설치 가이드` |
| `parent` | 부모 페이지 제목 | `시작하기` |
| `nav_order` | 정렬 순서 (작을수록 위) | `1` |
| `has_children` | 자식 페이지 여부 | `true` |
| `permalink` | 고정 URL | `/docs/my-page/` |

### 4. 마크다운 작성 팁

#### 코드 블록

````markdown
```python
def hello():
    print("Hello!")
```
````

#### 표

```markdown
| 열1 | 열2 |
|-----|-----|
| A   | B   |
```

#### 알림 박스

```markdown
{: .note }
> 참고 내용입니다.

{: .warning }
> 주의 내용입니다.
```

---

## 명령어

```bash
# 로컬 서버 실행
make local

# 배포
make prod msg="새 글 추가"

# 의존성 설치
make install

# 캐시 삭제
make clean
```

---

## 프로젝트 설정

프로젝트 초기 설정 방법은 [blog-setup.md](blog-setup.md) 참고
