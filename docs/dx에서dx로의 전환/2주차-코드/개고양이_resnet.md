---
layout: default
title: 개고양이_resnet.py
parent: 2주차 코드
grand_parent: DX 전환
nav_order: 16
---

# 개고양이_resnet.py

ResNet50 전이학습을 활용한 개/고양이 분류

## 핵심 개념
- 전이학습 (Transfer Learning)
- ResNet50 사전학습 모델
- 특성 추출 (Feature Extraction)
- 데이터 증강
- 이진 분류

```python
import os, shutil, pathlib
import tensorflow as tf

original_dir = pathlib.Path("./dogs-vs-cats/train")
new_base_dir = pathlib.Path("./dogs-vs-cats/cats_vs_dogs_small")

def make_subset(subset_name, start_index, end_index):
    for category in ("cat", "dog"):
        dir = new_base_dir / subset_name / category
        os.makedirs(dir)
        fnames = [f"{category}.{i}.jpg" for i in range(start_index, end_index)]
        for fname in fnames:
            shutil.copyfile(src=original_dir / fname,
                            dst=dir / fname)

# 데이터셋 로드
from tensorflow.keras.utils import image_dataset_from_directory

train_dataset = image_dataset_from_directory(
    new_base_dir / "train",
    image_size=(180, 180),
    batch_size=16)

validation_dataset = image_dataset_from_directory(
    new_base_dir / "validation",
    image_size=(180, 180),
    batch_size=16)

test_dataset = image_dataset_from_directory(
    new_base_dir / "test",
    image_size=(180, 180),
    batch_size=16)

import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow import keras

# 데이터 증강
data_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.2),
    ]
)

# ResNet50 사전학습 모델 로드 (분류층 제외)
conv_base = tf.keras.applications.ResNet50(
    include_top=False,
    weights="imagenet",
    input_shape=(180, 180, 3)
)
conv_base.summary()

# 특성 추출
def get_features_and_labels(dataset):
    all_features = []
    all_labels = []
    for images, labels in dataset:
        preprocessed_images = keras.applications.vgg16.preprocess_input(images)
        features = conv_base.predict(preprocessed_images)
        all_features.append(features)
        all_labels.append(labels)
    return np.concatenate(all_features), np.concatenate(all_labels)

train_features, train_labels = get_features_and_labels(train_dataset)
val_features, val_labels = get_features_and_labels(validation_dataset)
test_features, test_labels = get_features_and_labels(test_dataset)

# 분류 모델 구축
inputs = keras.Input(shape=(6, 6, 2048))
x = data_augmentation(inputs)
x = layers.Flatten()(inputs)
x = layers.Dense(256)(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)
model = keras.Model(inputs, outputs)

model.compile(loss="binary_crossentropy",
              optimizer="rmsprop",
              metrics=["accuracy"])

callbacks = [
    keras.callbacks.ModelCheckpoint(
      filepath="feature_extraction.keras",
      save_best_only=True,
      monitor="val_loss")
]

history = model.fit(
    train_features, train_labels,
    epochs=3,
    validation_data=(val_features, val_labels),
    callbacks=callbacks)
```

## 전이학습 구조

```
ResNet50 (ImageNet 사전학습)
    ↓
특성 추출 (conv_base.predict)
    ↓
Flatten → Dense(256) → Dropout(0.5) → Dense(1, sigmoid)
    ↓
이진 분류 (개/고양이)
```
