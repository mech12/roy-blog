---
layout: default
title: 1주차 - AX 시대
parent: DX 전환
nav_order: 1
---

# 1주차: AX 시대 (머신러닝 개요)

## 이론 자료

[📥 1주차-ax시대.pptx 다운로드](1주차-ax시대.pptx)

---

## 실습: 머신러닝 기초

### 환경 설정

```bash
# Anaconda 가상환경 생성
conda create --name myenv python=3.9

# 가상환경 활성화
conda activate myenv

# 필요 라이브러리 설치
pip install numpy scikit-learn
```

### 실습 코드: Iris 분류 (로지스틱 회귀)

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# 1. 데이터 불러오기
iris = load_iris()
X = iris.data
y = iris.target
target_names = iris.target_names

print("✅ 아이리스 데이터 로드 완료")
print(f"특징(Feature)의 수: {X.shape[1]}")
print(f"타겟 클래스: {target_names}")

# 2. 학습/테스트 데이터 분리 (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 3. 로지스틱 회귀 모델 학습
model = LogisticRegression(
    solver='liblinear',
    multi_class='ovr',
    random_state=42
)
model.fit(X_train, y_train)

# 4. 예측 및 평가
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n모델 정확도: {accuracy * 100:.2f}%")
print(classification_report(y_test, y_pred, target_names=target_names))

# 5. 새로운 데이터 예측
new_flower = np.array([[6.1, 3.0, 4.5, 1.5]])
prediction = model.predict(new_flower)
print(f"예측 결과: {target_names[prediction[0]]}")
```

### 핵심 개념

| 용어 | 설명 |
|------|------|
| **지도 학습** | 레이블(정답)이 있는 데이터로 학습 |
| **로지스틱 회귀** | 분류 문제를 위한 선형 모델 |
| **train_test_split** | 데이터를 학습/테스트 세트로 분리 |
| **accuracy_score** | 모델의 정확도 측정 |

### 실습 파일

**[전체 실습 코드 보기](1주차-코드/)** - 클릭하면 소스 코드 확인 가능

| 파일 | 설명 |
|------|------|
| [hello.py](1주차-코드/hello) | Python 기초 - 첫 번째 프로그램 |
| [머신러닝1.py](1주차-코드/머신러닝1) | Iris 꽃 분류 (로지스틱 회귀) |
