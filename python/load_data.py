# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 13:44:48 2022

@author: mauricio.jurado
"""

# Imports

import cv2
import os
from sys import exit
import pandas as pd
import warnings

from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

def load_test_train(path='C:/Users/mauricio.jurado/Desktop/capstone/exit/'):
    
    train = pd.read_csv(path + 'train.csv')
    test = pd.read_csv(path + 'test.csv')
    
    return train['data'], train['labels'], test['data'], test['labels'] #X_train, Y_train, x_test, y_test
    

def load_test_train_reshuffled(path='C:/Users/mauricio.jurado/Desktop/capstone/exit/'):
    
    complete = pd.read_csv(path + 'complete.csv')
    
    return train_test_split(complete['data'], complete['labels'], test_size=0.25)

def load_test_train_csv(path='C:/Users/mauricio.jurado/Desktop/capstone'):
    
    train = pd.DataFrame(columns=['data', 'labels'])
    test = pd.DataFrame(columns=['data', 'labels'])
    
    train = load_imgs(train, path + '/train/closed/')
    train = load_imgs(train, path + '/train/open/')
    
    test = load_imgs(test, path + '/test/closed/')
    test = load_imgs(test, path + '/test/open/')
    
    train.to_csv(path + '/exit/train.csv', index= False)
    test.to_csv(path + '/exit/test.csv', index= False)
    
    pd.concat([train, test]).to_csv(path + '/exit/complete.csv', index= False)
    
    return train['data'], train['labels'], test['data'], test['labels'] #X_train, Y_train, x_test, y_test
    
def load_imgs(array, path):
    
    for file in os.listdir(path):
        
        img = cv2.imread(path + file)
        aux = pd.DataFrame({'data': [img], 'labels': path.split('/')[-2]})
        array = pd.concat([array, aux])
        
    return array
    