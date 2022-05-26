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

from kafka_arc import Consumer

def main():
    consumer = Consumer('testing321','localhost:9092',2, "grupo_1")
    consumer.consume_camera()
    
if __name__ == '__main__':
    
    main()