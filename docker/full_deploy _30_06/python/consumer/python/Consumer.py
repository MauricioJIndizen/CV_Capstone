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
import os
import pandas as pd
import time
import torch

###############
# SORTED LIST #
###############

def start_alert(n):
    print('START ' + str(n))
    
def end_alert(n):
    print('END ' + str(n))

class sorted_list():
    
    def __init__(self, max_len, order_position):
        self.max_len = max_len
        self.order_position = order_position
        self.current_len = 0
        self.check_wait = 0
        self.max_check_wait = 5
        self.alert = False
        self.iter = 0
        
        self.list = []
        
    def append(self, value):
        
        self.iter += 1
        
        if self.current_len < self.max_len:
            self.current_len += 1
        else:
            self.list.pop(0)
            
        self.list.append(value)
        sorted(self.list, key=lambda x:x[1])

        self.check_wait += 1
        if self.check_wait == self.max_check_wait:
            self.check_wait = 0
            asleep = self.check_drowsy()
            if self.alert and not asleep:
                self.alert = False
                end_alert(self.iter)
            else:
                if not self.alert and asleep:
                    self.alert = True
                    start_alert(self.iter)

    def check_drowsy(self):
        
        flag = True
        for x in self.list:
            if 'OPENED' in x[2]:
                flag = False
                break
        
        return flag
    
    def get_len(self):
        return len(self.list)

class Consumer():
    
    def __init__(self, topic, broker, id, group):
        self.consumer = KafkaConsumer(topic, bootstrap_servers=broker, consumer_timeout_ms=300000, group_id = group, api_version=(0,10,2), auto_offset_reset='earliest')
        self.id = id
        self.server = broker
        
    def consume_results(self):
        print("Consumer " + str(self.id) + " connected")
        num_frames = 60
        
        window = sorted_list(90, 1)
        
        for message in self.consumer:
            nparr = message.value.decode()
            if num_frames == 60:
                start = time.time()
            elif num_frames == 0:
                num_frames = 61
                end = time.time()
                seconds = end - start
                print ("Time taken : {0} seconds".format(seconds))
                # Calculate frames per second
                fps  = 60 / seconds
                print("Estimated frames per second : {0}".format(fps))
            num_frames = num_frames - 1
            id = nparr.split(";")[0]
            dt = nparr.split(";")[1]
            results = nparr.split(";")[2]
            print("Topic receive new message from Consumer " + id + ", with timestamp " + dt + ", and results " + results)
            
            window.append(nparr)

    def consume_text(self):
        print("Consumer " + str(self.id) + " connected")
        for msg in self.consumer:
            nparr = np.frombuffer(msg.value, np.uint8)
            print("Consumer " + str(self.id) + "receive: " + str(nparr))

    def consume_camera(self, result_broker):   
        actual_directory = os.getcwd()
        #clf_path = os.path.join(actual_directory,'model\clf')
        yolo_path = os.path.join(actual_directory,'model\yolo')
        #clf_model_name = os.path.join(clf_path,'eye_classifier1_v5.h5')
        yolo_directory = os.path.join(yolo_path,'ultralytics_yolov5_master')
        yolo_model_name = os.path.join(yolo_path,'yolov2.pt')
       
        #print(clf_model_name)
        #clf_model = load_model(clf_model_name)
        yolo_model = torch.hub.load(yolo_directory, 'custom', path=yolo_model_name, source = "local",force_reload=True)
        print('Consuming web_cam')
        num_frames = 60
        producer = KafkaProducer(bootstrap_servers=result_broker, api_version=(0,10,2))
        try:
            for message in self.consumer:
                nparr = np.frombuffer(message.value, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                dt = str(message.timestamp)
                result = yolo_model(frame)        
                df = result.pandas().xyxy[0]
                result_eyes = []
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if num_frames == 60:
                    start = time.time()
                elif num_frames == 0:
                    num_frames = 61
                    end = time.time()
                    seconds = end - start
                    print ("Time taken : {0} seconds".format(seconds))
                    # Calculate frames per second
                    fps  = 60 / seconds
                    print("Estimated frames per second : {0}".format(fps))
                for j in range(len(df)):
                    if float(df["confidence"][j]) > 0.5:
                        xmin = int(df["xmin"][j])
                        xmax = int(df["xmax"][j])
                        ymin = int(df["ymin"][j])
                        ymax = int(df["ymax"][j])
                        clas = int(df["class"][j])
                        result = "OPENED" if clas == 0 else "CLOSED "
                        result_eyes.append(result)
                        text_x = int(xmin)
                        text_y = int(ymin-20)
                        #DRAW TEXT OVER EYES
                        cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),color=(255, 0, 0), thickness=3)
                        cv2.putText(frame, result, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1, cv2.LINE_AA)
                filename = dt + ".jpg"
                save_path = os.path.join(actual_directory,"images")
                if os.path.isdir(save_path) == False:
                    os.makedirs(save_path)
                cv2.imwrite(os.path.join(save_path,filename),frame)
                text = str(self.id) 
                data = text + ";" + dt + ";" + str(result_eyes)
                buffer = str.encode(data)
                print(data)
                producer.send("capstone_drowsiness_output", buffer)
                producer.flush()
                num_frames = num_frames - 1
        except Exception as e:
            print('#############################')
            print(e)
            print('#############################')
            exit(1)
                    
