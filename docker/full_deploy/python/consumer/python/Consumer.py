# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:11:38 2022

@author: mauricio.jurado
"""

import sys
import cv2
import numpy as np
from datetime import datetime
from kafka import  KafkaConsumer, KafkaProducer
from keras.models import load_model
from skimage.transform import resize
import os
import pandas as pd
import time
import torch
from keras.models import load_model


class Consumer():
    
    def __init__(self, topic, broker, id, group):
        self.consumer = KafkaConsumer(topic, bootstrap_servers=broker, consumer_timeout_ms=30000, group_id = group, api_version=(0,10,2), auto_offset_reset='earliest')
        self.id = id
        self.server = broker
        
    def consume_results(self):
        print("Consumer " + str(self.id) + " connected")
        num_frames = 120
        for message in self.consumer:
            nparr = np.frombuffer(message.value, np.uint8)
            print("Topic receive new message")
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
            num_frames = num_frames - 1

    def consume_text(self):
        print("Consumer " + str(self.id) + " connected")
        for msg in self.consumer:
            nparr = np.frombuffer(msg.value, np.uint8)
            print("Consumer " + str(self.id) + "receive: " + str(nparr))

    def consume_camera(self):   
        actual_directory = os.path.join(os.getcwd(), 'python\consumer\python')

        clf_path = os.path.join(actual_directory,'model\clf')
        yolo_path = os.path.join(actual_directory,'model\yolo')
        clf_model_name = os.path.join(clf_path,'eye_classifier1_v3.h5')
        yolo_directory = os.path.join(yolo_path,'ultralytics_yolov5_master')
        yolo_model_name = os.path.join(yolo_path,'yolo.pt')
       
        clf_model = load_model(clf_model_name)
        yolo_model = torch.hub.load(yolo_directory, 'custom', path=yolo_model_name, source = "local",force_reload=True)
      
        print('Consuming web_cam')
        num_frames = 120
        try:
            for message in self.consumer:
                nparr = np.frombuffer(message.value, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                result = yolo_model(frame)        
                df = result.pandas().xyxy[0]
                for j in range(len(df)):
                    if float(df["confidence"][j]) > 0.5:
                        xmin = int(df["xmin"][j])
                        xmax = int(df["xmax"][j])
                        ymin = int(df["ymin"][j])
                        ymax = int(df["ymax"][j])
                        eye_image = frame[ymin:ymax, xmin:xmax]
                        eye_scaled = resize(eye_image, (80, 80), preserve_range=True).astype(np.uint8)
                        eye_scaled_norm = eye_scaled.astype("float32") / 255
                        out_probabilities = clf_model.predict(np.reshape(eye_scaled_norm,(1,80,80,3)))
                        result = "OPENED" + str(out_probabilities[0][0]) if out_probabilities[0][0] > 0.5 else "CLOSED " + str(out_probabilities[0][0])
                        result = "OPENED" if out_probabilities[0][0] > 0.5 else "CLOSED "
                        text_x = int(xmin)
                        text_y = int(ymin-20)
                        #DRAW TEXT OVER EYES
                        cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),color=(255, 0, 0), thickness=3)
                        cv2.putText(frame, result, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1, cv2.LINE_AA)
                producer = KafkaProducer(bootstrap_servers=self.server, api_version=(0,10,2))
                text = str(self.id) 
                buffer = str.encode(text)
                producer.send("results", buffer)
                producer.flush()
        except Exception as e:
            print('#############################')
            print(e)
            print('#############################')
            exit(1)
                    
