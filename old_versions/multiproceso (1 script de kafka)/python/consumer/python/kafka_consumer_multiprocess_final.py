from http import server
import logging
import numpy as np
import json
import io
import os
import sys
from kafka import KafkaConsumer, KafkaProducer
import multiprocessing
from datetime import datetime
import time 
import cv2
from skimage.transform import resize
import torch
from keras.models import load_model

class Consumer(multiprocessing.Process):
    daemon = True
            
    def __init__(self,topic,server,id):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        self.id = id
        self.server = server
        self.topic = topic
    
    def stop(self):
        self.stop_event.set()

    def run(self):
        clf_model = load_model('model/clf/eye_classifier1_v3.h5')
        yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path='model/yolo/yolo.pt', force_reload=True)
        try:
            consumer = KafkaConsumer(bootstrap_servers=self.server,
                                 enable_auto_commit=True,
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=30000,
                                 group_id  = "consumer-group",
                                 api_version = (0,9))
            consumer.subscribe([self.topic])
            while not self.stop_event.is_set():
                for message in consumer:
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
                    if self.stop_event.is_set():
                        break
            consumer.close()
        except IOError as exception:
            print("Read error")
            logging.info("Issue with getting data from queue" )
            logging.error(exception)

