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

from Consumer import Consumer

def main():
    consumer = Consumer('capstone_drowsiness_output','localhost:9092',1, "grupo_resultados")
    consumer.consume_results()
    
if __name__ == '__main__':
    
    main()