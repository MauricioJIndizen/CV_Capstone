# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:11:38 2022

@author: mauricio.jurado
"""

import sys
import time
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from kafka import KafkaProducer, KafkaConsumer

class Producer():

    def __init__(self, topic):
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        
    def publish_camera(self):
    
        print("publishing feed!")
        camera = cv2.VideoCapture(0)
        try:
            while(True):
                success, frame = camera.read()
            
                ret, buffer = cv2.imencode('.jpg', frame)
                self.producer.send(self.topic, buffer.tobytes())
                #self.producer.send(self.topic, 'hello there')
                #self.producer.flush()
                
                # Choppier stream, reduced load on processor
                time.sleep(0.2)
    
        except:
            print("\nExiting.")
            sys.exit(1)
        finally:
            camera.release()

class Consumer():
    
    def __init__(self, topic):
        self.consumer = KafkaConsumer(topic, bootstrap_servers='localhost:9092', consumer_timeout_ms=3000)
        
    def consume_camera(self):   
        i = 0
        print('Consuming web_cam')
        for msg in self.consumer:
            
            try:
                
                nparr = np.frombuffer(msg.value, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                cv2.imwrite('wcam_imgs/' + str(i) + '.jpg', img)
                i += 1
                
            except Exception as e:
                print('#############################')
                print(e)
                print('#############################')
                exit(1)
                    
                