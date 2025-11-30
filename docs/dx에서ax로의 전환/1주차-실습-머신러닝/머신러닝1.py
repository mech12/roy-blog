import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

# 1. 데이터 불러오기 및 준비
## scikit-learn에 내장된 아이리스 데이터셋을 불러옵니다.
iris = load_iris()

# 특징(X)과 타겟(y) 분리
X = iris.data  
y = iris.target 
target_names = iris.target_names

print("✅ 아이리스 데이터 로드 완료")
print(f"특징(Feature)의 수: {X.shape[1]}")
print(f"타겟 클래스: {target_names}")

# 2. 학습용 데이터와 테스트용 데이터 분리
## 데이터를 학습(80%)과 테스트(20%) 세트로 무작위 분할합니다.
# 로지스틱 회귀는 선형 모델이므로, 데이터 스케일링이 필요할 수 있지만, 
# 아이리스 데이터는 단순하여 여기서는 생략하고 진행합니다.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,      # 테스트 데이터 비율 20%
    random_state=42,    # 재현성을 위한 난수 시드 설정
    stratify=y          # 타겟 클래스의 비율을 유지하며 분할
)

print(f"학습 데이터 개수: {len(X_train)}")
print(f"테스트 데이터 개수: {len(X_test)}")

# 3. 로지스틱 회귀 모델 생성 및 학습 (훈련)
## 다중 클래스 분류를 위한 로지스틱 회귀 모델을 생성합니다.
## solver='liblinear'는 작은 데이터셋에 적합하며 다중 클래스에 잘 작동합니다.
model = LogisticRegression(
    solver='liblinear',
    multi_class='ovr', # One-vs-Rest 방식으로 다중 클래스 분류를 수행
    random_state=42
)

## 학습 데이터(X_train, y_train)를 사용하여 모델을 훈련시킵니다.
model.fit(X_train, y_train)

print("\n✅ 로지스틱 회귀 모델 학습 완료")

# 4. 예측 및 평가
## 테스트 데이터(X_test)를 사용하여 예측을 수행합니다.
y_pred = model.predict(X_test)

## 실제 정답(y_test)과 예측 결과(y_pred)를 비교하여 정확도를 계산합니다.
accuracy = accuracy_score(y_test, y_pred)

print("\n--- 모델 성능 평가 ---")
print(f"모델의 정확도: {accuracy * 100:.2f}%")

# 더 자세한 성능 보고서 출력 (정밀도, 재현율 등)
print("\n--- 상세 분류 보고서 ---")
print(classification_report(y_test, y_pred, target_names=target_names))

# 5. 새로운 데이터 예측 예시
print("\n--- 새로운 데이터로 예측해보기 ---")
# [꽃받침 길이, 꽃받침 폭, 꽃잎 길이, 꽃잎 폭]을 가진 새로운 꽃 데이터
new_flower = np.array([[6.1, 3.0, 4.5, 11.5]]) 

# 모델을 사용하여 예측
prediction = model.predict(new_flower)

# 예측 결과 출력 (숫자를 타겟 이름으로 변환하여 출력)
predicted_species = target_names[prediction[0]]
print(f"새로운 꽃의 특징: {new_flower}")
print(f"예측된 꽃의 종류: {predicted_species}")