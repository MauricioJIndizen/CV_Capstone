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
import os

from Consumer import Consumer

def main():
    consumer = Consumer('capstone_drowsiness_intake','127.0.0.1:9092',1, "grupo_1")
    consumer.consume_camera()
    
if __name__ == '__main__':
    
    print(os.getcwd())
    main()