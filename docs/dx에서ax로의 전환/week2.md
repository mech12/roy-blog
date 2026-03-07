---
layout: default
title: 2주차 - 딥러닝
parent: DX 전환
grand_parent: 비트교육센터
nav_order: 2
has_children: true
---

# 2주차: 딥러닝 종합

## 이론 자료

[📥 2주차-딥러닝_종합.ppt 다운로드](2주차-딥러닝_종합.ppt)

---

## 실습: 딥러닝 기초

### 환경 설정

```bash
conda activate myenv

# TensorFlow 설치
pip install tensorflow
```

### 실습 1: Iris 딥러닝 분류

```python
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras import models, layers
from tensorflow.keras.utils import to_categorical
import numpy as np

tf.random.set_seed(2)

# 1. 데이터 준비
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris['data'], iris['target'], random_state=0
)

# 2. 딥러닝 모델 구축
network = models.Sequential()
network.add(layers.Dense(64, activation="relu", input_shape=(4,)))
network.add(layers.Dense(3, activation="softmax"))

network.compile(
    optimizer="sgd",
    loss="categorical_crossentropy",
    metrics=['accuracy']
)

# 3. 데이터 전처리
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# 원핫 인코딩
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

# 4. 학습
network.fit(X_train, y_train, epochs=10, batch_size=100)

# 5. 평가
train_loss, train_acc = network.evaluate(X_train, y_train)
test_loss, test_acc = network.evaluate(X_test, y_test)
print(f"테스트 정확도: {test_acc * 100:.2f}%")

# 6. 예측
y_pred = network.predict(X_test)
y_pred = np.argmax(y_pred, axis=1)
```

### 핵심 개념

| 용어 | 설명 |
|------|------|
| **Sequential** | 층을 순차적으로 쌓는 모델 |
| **Dense** | 완전 연결 층 (Fully Connected Layer) |
| **ReLU** | 활성화 함수: max(0, x) |
| **Softmax** | 다중 분류를 위한 출력 활성화 함수 |
| **categorical_crossentropy** | 다중 분류 손실 함수 |
| **원핫 인코딩** | 클래스를 벡터로 변환 (0→[1,0,0]) |

### 실습 파일 목록

**[전체 실습 코드 보기](2주차-코드/)** - 클릭하면 소스 코드 확인 가능

| 파일 | 설명 |
|------|------|
| [iris딥러닝.py](2주차-코드/iris딥러닝) | Iris 데이터 딥러닝 분류 |
| [손글씨.py](2주차-코드/손글씨) | MNIST CNN 분류 |
| [개고양이_new.py](2주차-코드/개고양이_new) | CNN 이미지 분류 + 데이터 증강 |

### 딥러닝 모델 구조

```
입력층 (4개 특징)
    ↓
Dense(64, ReLU)  ← 은닉층
    ↓
Dense(3, Softmax) ← 출력층 (3개 클래스)
```
