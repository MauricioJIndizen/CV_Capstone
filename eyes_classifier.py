import numpy as np
import cv2
from keras.models import load_model
from skimage.transform import resize
import os
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
from utils import *

#LOAD HAAR CASCADE MODELS TO DETECT FACE AND EYES
face_cascade, eye_cascade = load_haarcascade()

#LAUNCH VIDEOCAMARA
cap = cv2.VideoCapture(0)
model = load_model('model/eye_classifier1.h5')

fontScale = 1
font = cv2.FONT_HERSHEY_PLAIN
thickness = 2

while 1:

    #READING IMAGE FROM VIDEOCAMERA
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #DETECT FACES FROM IMAGE
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    #LOOP FOR FACES
    for (x,y,w,h) in faces:
        #DRAW RECTANGLE OVER FACES
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

        #REDUCE IMAGE TO ONLY FACE
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        #DETECT EYES ON FACE IMAGE
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:

            eye_color = roi_color[ey:ey+eh, ex:ex+ew]
            #RESIZE IMAGE FOR NN EYE CLASSIFIER (OPENED OR CLOSED)
            eye_color_scaled = resize(eye_color, (200, 200), preserve_range=True).astype(np.uint8)
            #DRAW RECTANGLE OVER EYES
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            #PREDICT IF EYE IS OPENED OR CLOSED
            out_probabilities = model.predict(np.reshape(eye_color_scaled,(1,200,200,3)))
            result = "ABIERTO" if out_probabilities[0][0] > 0.5 else "CERRADO"
            text_x = int(ex+ew/4)
            text_y = int(ey-20)
            #DRAW TEXT OVER EYES
            cv2.putText(roi_color, result, (text_x, text_y), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
