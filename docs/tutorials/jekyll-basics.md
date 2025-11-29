---
layout: default
title: Jekyll 기초
parent: 튜토리얼
nav_order: 1
---

# Jekyll 기초

Jekyll 블로그의 기본 사용법을 알아봅니다.

## 새 페이지 추가하기

### 1. 파일 생성

`docs/` 폴더 아래에 `.md` 파일을 생성합니다.

### 2. Front Matter 작성

파일 상단에 다음과 같이 작성합니다:

```markdown
---
layout: default
title: 페이지 제목
parent: 부모 카테고리
nav_order: 1
---
```

### 3. 내용 작성

Front Matter 아래에 Markdown으로 내용을 작성합니다.

## 네비게이션 구조

| 속성 | 설명 |
|------|------|
| `title` | 네비게이션에 표시될 제목 |
| `parent` | 부모 페이지 제목 (트리 구조용) |
| `nav_order` | 정렬 순서 (숫자가 작을수록 위) |
| `has_children` | 자식 페이지 여부 (true/false) |

## 코드 블록

````markdown
```python
def hello():
    print("Hello, World!")
```
````

결과:

```python
def hello():
    print("Hello, World!")
```
