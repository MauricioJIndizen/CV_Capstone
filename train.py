import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow import keras
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from PIL import Image

from utils import *

print("Training model")

train_root = r'data/train'
test_root = r'data/test'

x_train, y_train = load_images(train_root)
x_test, y_test = load_images(test_root)

keras.backend.clear_session()
model = Sequential()
model.add(Conv2D(16, (3, 3), activation='relu',padding='same', input_shape=(200, 200, 3)))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(32, (3, 3), activation='relu',padding='same'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

change_lr_callback = CustomCallbackReduceLr()
history = model.fit(x_train, y_train, batch_size=10, epochs=50, verbose=1, validation_split=0.1, callbacks = [change_lr_callback])

results = model.evaluate(x_test, y_test)

print(results)