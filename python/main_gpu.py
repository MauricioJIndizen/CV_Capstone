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

from statistics import mean
from unittest import result
import torch
import time
import numpy as np
import cv2
from skimage.transform import resize
import math
import os
import platform
import subprocess
import time
import warnings
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from statistics import mean
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F

def main():
    device = select_device(0)
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolo.pt', force_reload=True)
    cap = cv2.VideoCapture(0)
    num_frames = 120
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
    while cap.isOpened():
        if num_frames == 120:
            total_start = time.time()
        elif num_frames == 0:
            num_frames = 121
            total_end = time.time()
            seconds = total_end - total_start
            print ("Time taken : {0} seconds".format(seconds))
            # Calculate frames per second
            fps  = 120 / seconds
            print("Estimated frames per second : {0}".format(fps))
        start = time.time()
        ret, frame = cap.read()
        result = model(frame)
        df = result.pandas().xyxy[0]
        if len(df)>2:
            df2 = df
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for j in range(len(df)):
            if float(df["confidence"][j]) > 0.5:
                xmin = int(df["xmin"][j])
                xmax = int(df["xmax"][j])
                ymin = int(df["ymin"][j])
                ymax = int(df["ymax"][j])
                cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),color=(255, 0, 0), thickness=3)
        end = time.time()
        elapsed = end - start
        print("Elapsed time: {0}".format(elapsed))
        num_frames = num_frames - 1
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    
def select_device(device='', batch_size=0, newline=True):
    # device = 'cpu' or '0' or '0,1,2,3'
    s = f'YOLOv5 🚀 torch {torch.__version__} '  # string
    device = str(device).strip().lower().replace('cuda:', '')  # to string, 'cuda:0' to '0'
    cpu = device == 'cpu'
    if cpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # force torch.cuda.is_available() = False
    elif device:  # non-cpu device requested
        os.environ['CUDA_VISIBLE_DEVICES'] = device  # set environment variable - must be before assert is_available()
        assert torch.cuda.is_available() and torch.cuda.device_count() >= len(device.replace(',', '')), \
            f"Invalid CUDA '--device {device}' requested, use '--device cpu' or pass valid CUDA device(s)"

    cuda = not cpu and torch.cuda.is_available()
    if cuda:
        devices = device.split(',') if device else '0'  # range(torch.cuda.device_count())  # i.e. 0,1,6,7
        n = len(devices)  # device count
        if n > 1 and batch_size > 0:  # check batch_size is divisible by device_count
            assert batch_size % n == 0, f'batch-size {batch_size} not multiple of GPU count {n}'
        space = ' ' * (len(s) + 1)
        for i, d in enumerate(devices):
            p = torch.cuda.get_device_properties(i)
            s += f"{'' if i == 0 else space}CUDA:{d} ({p.name}, {p.total_memory / (1 << 20):.0f}MiB)\n"  # bytes to MB
    else:
        s += 'CPU\n'

    if not newline:
        s = s.rstrip()
    return torch.device('cuda:0' if cuda else 'cpu')

if __name__ == '__main__':
    
    main()