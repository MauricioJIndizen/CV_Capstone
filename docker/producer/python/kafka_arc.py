# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:11:38 2022

@author: mauricio.jurado
"""

import sys
import time
import cv2
from datetime import datetime
from kafka import KafkaProducer

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


                