# -*- coding: utf-8 -*-
"""
Created on Fri May  6 10:18:52 2022

@author: mauricio.jurado
"""

from kafka_arc import *
import numpy as np
import pandas as pd
import cv2
import time
import datetime
from utils import *

def main_camera():
    id = 1
    servers = ['localhost:9092']    
    producers = []
    topic = "testing321"
    for server in servers:
        producers.append(Producer(topic,server,id))
        id += 1
    print("Publishing feed!")
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    num_frames = 120
    producer_index = 0
    try:
        while(True):
            success, frame = camera.read()
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
            #dt = str(datetime.now())
            #frame = cv2.putText(image, dt, (0,20), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.0, color = (255,0,0), thickness = 1, lineType = cv2.LINE_AA)
            producers[producer_index].send_camera(frame)
            if producer_index < len(producers)-1 and len(producers) > 1:
                producer_index += 1
            else:
                producer_index = 0
            num_frames = num_frames - 1    
    except Exception as e:
        print(e)
        print("\nExiting.")
        camera.release()
        cv2.destroyAllWindows()
def main():
    id = 1
    #servers = ['localhost:9091','localhost:9092','localhost:9093','localhost:9094','localhost:9095']
    servers = ['20.86.145.231:9092']
    producers = []
    for server in servers:
        topic = "testing321"
        producers.append(Producer(topic,server,id))
        id += 1
    producer_index = 0
    for i in range(10000):
        text = str(i) 
        producers[producer_index].send_text(text)
        if producer_index < len(producers)-1 and len(producers) > 1:
            producer_index += 1
        else:
            producer_index = 0
if __name__ == '__main__':
    
    main()