# -*- coding: utf-8 -*-
"""
Created on Fri May  6 10:18:52 2022

@author: mauricio.jurado
"""

from kafka_arc import *

def main():
    producer = Producer('testing')
    producer.publish_camera()
    
if __name__ == '__main__':
    
    main()