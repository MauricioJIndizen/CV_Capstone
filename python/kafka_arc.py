# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:11:38 2022

@author: mauricio.jurado
"""

import sys
import time
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
from io import BytesIO
from kafka import KafkaProducer, KafkaConsumer
from keras.models import load_model
from skimage.transform import resize
import os
import pandas as pd
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from sklearn.preprocessing import LabelEncoder
import time
from utils import *

class Producer():

    def __init__(self, topic):
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        
    def publish_camera(self):
    
        print("publishing feed!")
        camera = cv2.VideoCapture(0)
        num_frames = 120
        try:
            while(True):
                success, image = camera.read()
                if num_frames == 120:
                    start = time.time()
                elif num_frames == 0:
                    num_frames = 121
                    end = time.time()
                    seconds = end - start
                    print ("Time taken : {0} seconds".format(seconds))
                    # Calculate frames per second
                    fps  = 120 / seconds
                    print("Estimated frames per second : {0}".format(fps))
                dt = str(datetime.now())
                frame = cv2.putText(image, dt, (0,20), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.0, color = (255,0,0), thickness = 1, lineType = cv2.LINE_AA)
                ret, buffer = cv2.imencode('.jpg', frame)
                self.producer.send(self.topic, buffer.tobytes())
                #self.producer.send(self.topic, 'hello there')
                #self.producer.flush()
                
                # Choppier stream, reduced load on processor
                num_frames = num_frames - 1    
        except Exception as e:
            print(e)
            print("\nExiting.")
            camera.release()
            cv2.destroyAllWindows()
        
        sys.exit(1)

class Consumer():
    
    def __init__(self, topic):
        self.consumer = KafkaConsumer(topic, bootstrap_servers='localhost:9092', consumer_timeout_ms=3000)
        
    def consume_camera(self):   
        face_cascade, eye_cascade = load_haarcascade()
        model = load_model('model/eye_classifier1.h5')
        i = 0
        print('Consuming web_cam')
        num_frames = 120
        for msg in self.consumer:
            if num_frames == 120:
                start = time.time()
            elif num_frames == 0:
                num_frames = 121
                end = time.time()
                seconds = end - start
                print ("Time taken : {0} seconds".format(seconds))
                # Calculate frames per second
                fps  = 120 / seconds
                print("Estimated frames per second : {0}".format(fps))
            try:
                nparr = np.frombuffer(msg.value, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                dt = str(datetime.now())
                #img = cv2.putText(img, dt, (0,50), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.0, color = (255,0,0), thickness = 1, lineType = cv2.LINE_AA)
                #cv2.imwrite('wcam_imgs/' + str(i) + '.jpg', img)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
                #DETECT FACES FROM IMAGE
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                #LOOP FOR FACES
                for (x,y,w,h) in faces:

                    #CROPPED IMAGE OF ONLY FACE
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = img[y:y+h, x:x+w]
                    
                    #DETECT EYES ON FACE IMAGE
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    
                    for (ex,ey,ew,eh) in eyes:
                        
                        #CROPPED IMAGE OF ONLY EYES
                        eye_color = roi_color[ey:ey+eh, ex:ex+ew]
                        
                        #RESIZE IMAGE FOR NN EYE CLASSIFIER (OPENED OR CLOSED)
                        eye_color_scaled = resize(eye_color, (200, 200), preserve_range=True).astype(np.uint8)
                        
                        #PREDICT IF EYE IS OPENED OR CLOSED
                        out_probabilities = model.predict(np.reshape(eye_color_scaled,(1,200,200,3)))
                        result = "OPENED" if out_probabilities[0][0] > 0.5 else "CLOSED"
                        text_x = int(ex+ew/4)
                        text_y = int(ey-20)
                        print("Classification result:: {0}".format(result))

                i += 1
                num_frames = num_frames - 1
            except Exception as e:
                print('#############################')
                print(e)
                print('#############################')
                exit(1)
                    
                