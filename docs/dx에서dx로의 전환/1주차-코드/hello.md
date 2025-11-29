---
layout: default
title: hello.py
parent: 1주차 코드
grand_parent: DX 전환
nav_order: 1
---

# hello.py

Python 첫 번째 프로그램 - Hello World

---

## 소스 코드

```python
print("Hello python")
```

---

## 설명

### `print()` 함수

Python에서 화면에 텍스트를 출력하는 가장 기본적인 함수입니다.

| 요소 | 설명 |
|-----|------|
| `print()` | 내장 함수 - 괄호 안의 내용을 화면에 출력 |
| `"Hello python"` | 문자열 (String) - 큰따옴표 또는 작은따옴표로 감싸서 표현 |

---

## 실행 방법

```bash
# 가상환경 활성화
conda activate myenv

# 실행
python hello.py
```

---

## 출력 결과

```
Hello python
```

---

## 다양한 print() 사용법

```python
# 1. 기본 출력
print("Hello python")

# 2. 여러 값 출력 (쉼표로 구분)
print("Hello", "Python", "World")  # Hello Python World

# 3. 숫자 출력
print(123)
print(3.14)

# 4. 변수 출력
name = "Python"
print(name)

# 5. f-string 포맷팅 (Python 3.6+)
version = 3.9
print(f"Python 버전: {version}")

# 6. 줄바꿈 없이 출력
print("Hello", end=" ")
print("World")  # Hello World (같은 줄)
```
