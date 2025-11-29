---
layout: default
title: 개고양이_new.py
parent: 2주차 실습 코드
grand_parent: DX 전환
nav_order: 3
---

# 개고양이_new.py

개와 고양이 이미지 분류 - CNN + 데이터 증강

## 핵심 개념
- 데이터 증강 (Data Augmentation): RandomFlip, RandomRotation, RandomZoom
- Conv2D + MaxPooling2D 조합
- Dropout으로 과적합 방지
- 모델 저장/로드 (.keras 형식)
- 이진 분류 (binary_crossentropy)

```python
#conda env config vars unset deeplearning
#conda deactivate
#conda activate 환경이름
#conda info --envs  : 환경변수 확인
#conda clean --all
#conda update conda
#conda create -n mytensorflow python=3.11 -c conda-forge #conda-forge:새로운 레포지토리
#conda activate mytensorflow
#conda install -c conda-forge tensorflow numpy scikit-learn scipy pandas matplotlib # 여기에 당신의 프로젝트에 필요한 다른 라이브러리도 추가하세요 (예: scikit-learn, opencv 등)
#주의사항 : pip랑 conda 섞지 말것, conda 로 설치
#https://www.tensorflow.org/tutorials/images/classification
import os
import tensorflow as tf
import shutil
# Suppress TensorFlow INFO and WARNING messages
# Set TF_CPP_MIN_LOG_LEVEL to:
# 0 = Show all messages (default)
# 1 = Filter out INFO messages
# 2 = Filter out INFO and WARNING messages
# 3 = Filter out INFO, WARNING, and ERROR messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# If you also want to suppress Python's warnings module messages (less common for these specific TF warnings)
import warnings
warnings.filterwarnings('ignore') # Or 'default' or 'always' for specific types of warnings


import pickle
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import models
# 이미지 전처리 유틸리티 모듈
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import random
import PIL.Image as pilimg
import imghdr
import pandas as pd
import pickle
import keras

#tf.compat.v1.disable_eager_execution()


# 원본 데이터셋을 압축 해제한 디렉터리 경로-원래 이미지 있는 폴더
original_dataset_dir = './dataset/cats_and_dogs/train'

#옮길 위치
base_dir = './dataset/cats_and_dogs_small'

train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')

model_save_path_keras = 'cats_and_dogs_model.keras'
history_filepath = 'cats_and_dogs_history.pkl'

batch_size = 16  #한번에 불러오는 이미지 개수
img_height = 180 #이미지의 높이
img_width = 180  #이미지의 넓이



#-------------------------------------
train_cats_dir = os.path.join(train_dir, 'cats')
train_dogs_dir = os.path.join(train_dir, 'dogs')

test_cats_dir = os.path.join(test_dir, 'cats')
test_dogs_dir = os.path.join(test_dir, 'dogs')

validation_cats_dir = os.path.join(validation_dir, 'cats')
validation_dogs_dir = os.path.join(validation_dir, 'dogs')

#이미지 복사
def ImageCopyMove():
    #디렉토리내의 파일 개수 알아내기
    totalCount = len(os.listdir(original_dataset_dir))
    print("전체개수 : ", totalCount)
    # 소규모 데이터셋을 저장할 디렉터리

    # 반복적인 실행을 위해 디렉토리를 삭제합니다.
    if os.path.exists(base_dir):  #기존에 디렉토리가 존재하면 전부 지우기
        shutil.rmtree(base_dir, ignore_errors=True, onerror=None)

    #새로폴더만들기
    os.mkdir(base_dir) #없으면 만들기

    os.mkdir(train_dir)
    os.mkdir(validation_dir)
    os.mkdir(test_dir)

    os.mkdir(train_cats_dir)
    print( train_cats_dir)
    os.mkdir(train_dogs_dir)
    os.mkdir(validation_cats_dir)
    os.mkdir(validation_dogs_dir)
    os.mkdir(test_cats_dir)
    os.mkdir(test_dogs_dir)

    # 처음 1,000개의 고양이 이미지를 train_cats_dir에 복사합니다
    fnames = ['cat.{}.jpg'.format(i) for i in range(1000)]
    for fname in fnames:
            src = os.path.join(original_dataset_dir, fname)
            dst = os.path.join(train_cats_dir, fname)
            shutil.copyfile(src, dst)

    # 다음 500개 고양이 이미지를 validation_cats_dir에 복사합니다
    fnames = ['cat.{}.jpg'.format(i) for i in range(1000, 1500)]
    for fname in fnames:
            src = os.path.join(original_dataset_dir, fname)
            dst = os.path.join(validation_cats_dir, fname)
            shutil.copyfile(src, dst)

    # 다음 500개 고양이 이미지를 test_cats_dir에 복사합니다
    fnames = ['cat.{}.jpg'.format(i) for i in range(1500, 2000)]
    for fname in fnames:
            src = os.path.join(original_dataset_dir, fname)
            dst = os.path.join(test_cats_dir, fname)
            shutil.copyfile(src, dst)

    # 처음 1,000개의 강아지 이미지를 train_dogs_dir에 복사합니다
    fnames = ['dog.{}.jpg'.format(i) for i in range(1000)]
    for fname in fnames:
            src = os.path.join(original_dataset_dir, fname)
            dst = os.path.join(train_dogs_dir, fname)
            shutil.copyfile(src, dst)

    # 다음 500개 강아지 이미지를 validation_dogs_dir에 복사합니다
    fnames = ['dog.{}.jpg'.format(i) for i in range(1000, 1500)]
    for fname in fnames:
            src = os.path.join(original_dataset_dir, fname)
            dst = os.path.join(validation_dogs_dir, fname)
            shutil.copyfile(src, dst)

    # 다음 500개 강아지 이미지를 test_dogs_dir에 복사합니다
    fnames = ['dog.{}.jpg'.format(i) for i in range(1500, 2000)]
    for fname in fnames:
            src = os.path.join(original_dataset_dir, fname)
            dst = os.path.join(test_dogs_dir, fname)
            shutil.copyfile(src, dst)


def DataIncrease():
        #레이어들이 train_ds에서 읽어온 각 이미지에 실시간으로 무작위 변형을 적용하여,
        #모델이 매 에포크마다 원본 이미지와 약간씩 다른 버전의 이미지를 보게 만듭니다.
        #이를 통해 모델의 일반화 성능을 높이고 과적합(overfitting)을 줄일 수 있습니다.

        data_augmentation = keras.Sequential(
                [
                   layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
                        layers.RandomRotation(0.1),
                        layers.RandomZoom(0.1),
                ]
        )

        model = models.Sequential()

        model.add(layers.Rescaling(1./255))
        model.add(data_augmentation)
        model.add(layers.Conv2D(32, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Flatten())
        model.add(layers.Dropout(0.5)) #중간에 데이터 절반을 없애버림 - 과대적합을 막기 위해서
        model.add(layers.Dense(512, activation='relu'))
        model.add(layers.Dense(1, activation='sigmoid'))

        #원핫인코딩 안할때 - 이진분류일때 가능
        model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

        train_ds = tf.keras.utils.image_dataset_from_directory(
                train_dir,
                validation_split=0.2,
                subset="training",
                seed=123,
                image_size=(img_height, img_width),
                batch_size=batch_size)

        val_ds = tf.keras.utils.image_dataset_from_directory(
                train_dir,
                validation_split=0.2,
                subset="validation",
                seed=123,
                image_size=(img_height, img_width),
                batch_size=batch_size)

        epochs=100
        history = model.fit(
                train_ds,
                validation_data=val_ds,
                epochs=epochs
        )

        print("----------------------------")
        # #모델 저장하기

        try:
                model.save(model_save_path_keras)
                print(f"모델이 TensorFlow SavedModel (.keras) 형식으로 '{model_save_path_keras}'에 성공적으로 저장되었습니다.")
        except Exception as e:
                print(f"TensorFlow SavedModel 저장 중 오류 발생: {e}")

        try:
                with open(history_filepath, 'wb') as file:
                        pickle.dump(history.history, file)
                print(f"학습 히스토리가 '{history_filepath}'에 성공적으로 저장되었습니다.")
        except Exception as e:
                print(f"학습 히스토리 저장 중 오류 발생: {e}")


import numpy as np
def Predict():
    #1.학습된 모듈을 불러온다
    loaded_model_keras = None
    try:
        loaded_model_keras = keras.models.load_model(model_save_path_keras)
        print("모델 부르기 성공")
    except Exception as e:
        print(f"모델 로딩중 실패 : {e}")
        return

    #예측데이터셋
    val_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=0.2,
        seed=123,
        subset="validation",
        image_size=(180,180),
        batch_size=16
    )

    print("----- 라벨링 ------")
    class_names = val_ds.class_names
    print(class_names)

    total_match_count =0
    total_samples_proceed=0
    max_samples_to_process = 500
    for input_batch, labels_batch in val_ds:
        total_samples_proceed += len(labels_batch)

        #예측하기
        prdictions_batch = loaded_model_keras.predict(input_batch, verbose=2)
        print(prdictions_batch)

        predicted_classes = (prdictions_batch>0.5).astype(int)
        print("예측 : ", predicted_classes.flatten())
        print("라벨 : ", labels_batch.numpy())

        match_count = np.sum(predicted_classes.flatten()== labels_batch.numpy() )
        total_match_count+= match_count

    print("전체데이터개수 ", total_samples_proceed)
    print("맞춘개수 ", total_match_count)
    print("못맞춘개수 ", total_samples_proceed-total_match_count)




def LoadModels():

    print("\n--- 저장된 모델 로드 테스트 ---")
    loaded_model_keras = None
    try:
        loaded_model_keras = keras.models.load_model(model_save_path_keras)
        print(f"모델이 '{model_save_path_keras}'에서 성공적으로 로드되었습니다.")
    except Exception as e:
        print(f"모델 로드 중 오류 발생: {e}")

    try:
        with open(history_filepath, 'rb') as file:
            history = pickle.load(file)
            print(f"학습 히스토리가 '{history_filepath}'에 성공적으로 불러왔습니다.")
    except Exception as e:
            print(f"학습 히스토리 읽는 중 오류 발생: {e}")
            return False

    acc = history['accuracy']
    val_acc = history['val_accuracy']
    loss = history['loss']
    val_loss = history['val_loss']

    epochs = range(len(acc))

    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.legend()

    plt.figure()

    plt.plot(epochs, loss, 'bo', label='Training loss')
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()

    plt.show()



if __name__=="__main__":
        while(True):
                print("1. 이미지 복사")
                print("2. 데이터 학습 ")
                print("3. 모듈 로딩하기")
                print("4. 예측하기 ")

                sel = input("선택 : ")
                if sel=="1":
                        ImageCopyMove()
                elif sel=="2":
                        DataIncrease()
                elif sel=="3":
                        LoadModels()
                elif sel=="4":
                        Predict()
                else:
                        break
```
