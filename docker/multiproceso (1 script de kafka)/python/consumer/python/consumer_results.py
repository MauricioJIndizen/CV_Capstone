# -*- coding: utf-8 -*-
"""
Created on Fri May  6 10:19:58 2022

@author: mauricio.jurado
"""

# -*- coding: utf-8 -*-
"""
Created on Fri May  6 10:18:52 2022

@author: mauricio.jurado
"""

from kafka import KafkaConsumer
import time
import numpy as np

def main():
    servers=['localhost:9092']
    topic = 'results'
    consumer0 = KafkaConsumer(bootstrap_servers=servers,
                                 enable_auto_commit=True,
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=30000)
    consumer0.subscribe([topic])
    num_frames = 120
    for message in consumer0:
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
    # start    
    # then stop

if __name__ == '__main__':
    
    main()