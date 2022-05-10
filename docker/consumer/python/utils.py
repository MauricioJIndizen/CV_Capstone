import numpy as np
import pandas as pd
from tensorflow import keras
import os
import cv2
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array

class CustomCallbackReduceLr(keras.callbacks.Callback):
    def __init__(self):
        self.val_accuracy = np.Inf
        self.accumulator = 0
    def on_epoch_begin(self, epoch, logs={}):
        if self.accumulator == 5:
            self.model.optimizer.lr = self.model.optimizer.lr*0.5
            self.accumulator = 0
            print("Changing Learning Rate to ", float(keras.backend.get_value(self.model.optimizer.lr)))
    def on_epoch_end(self, epoch, logs={}):
        current = logs["val_accuracy"]
        if (current - self.val_accuracy) < 0.05:
            self.accumulator = self.accumulator + 1
            print("No change on val accuracy, increment accumulator to ", self.accumulator)
        else:
            self.accumulator = 0
        self.val_accuracy = current

def load_images(root):
    data = []
    for category in sorted(os.listdir(root)):
        for file in sorted(os.listdir(os.path.join(root, category))):
            data.append((category, os.path.join(root, category,  file)))

    df = pd.DataFrame(data, columns=['class', 'file_path'])

    df['class'] = LabelEncoder().fit_transform(df['class'].values)
    photos, labels = list(), list()
    for index,row in df.iterrows():
        photo = load_img(row['file_path'], target_size=(200, 200))
        photo = img_to_array(photo)
        photo = photo.astype("float32") / 255
        photos.append(photo)
        labels.append(row['class'])
    X = np.asarray(photos)
    y = np.asarray(labels)
    return X, y

def load_haarcascade():
    face_cascade_name = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    eye_cascade_name = cv2.data.haarcascades + 'haarcascade_eye.xml'
    
    face_cascade = cv2.CascadeClassifier()
    if not face_cascade.load(cv2.samples.findFile(face_cascade_name)):
        print("Error loading xml file")
        exit(0)

    eye_cascade = cv2.CascadeClassifier()
    if not eye_cascade.load(cv2.samples.findFile(eye_cascade_name)):
        print("Error loading xml file")
        exit(0)
        
    return face_cascade, eye_cascade