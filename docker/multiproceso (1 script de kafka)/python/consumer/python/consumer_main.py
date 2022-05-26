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

from sys import api_version
from kafka_consumer_multiprocess_final import Consumer
from kafka import KafkaConsumer
import time
import torch
from keras.models import load_model
import pickle


def main():
    servers=['localhost:9092']
    topic = 'testing321'
    id = 1
    consumers1 = []
    consumer0 = KafkaConsumer(bootstrap_servers=servers,
                                 enable_auto_commit=True,
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=30000)
    consumer0.subscribe([topic])
    tp=len(consumer0.partitions_for_topic(topic))
    print(tp)
    consumer0.close()
    for i in range(tp):
        consumers1.append(Consumer(topic,servers,id))
        id += 1
    
    for consumer1 in consumers1:
        consumer1.start()
    # start

    time.sleep(400)
    
    # then stop
    for consumer1 in consumers1:
        consumer1.stop()
if __name__ == '__main__':
    
    main()