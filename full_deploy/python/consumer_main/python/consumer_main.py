# -*- coding: utf-8 -*-

from Consumer import *
import argparse

def parse_opt(known=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, default="capstone_drowsiness_intake" , help='Kafka topic where images are being sent')
    parser.add_argument('--server', type=str, default='localhost:9092', help='Kafka broker IP and port for retrieving images')
    parser.add_argument('--id', type=str, default="1", help='Consumer ID')
    parser.add_argument('--group', type=str, default="grupo_1", help='Name of consumer group')
    parser.add_argument('--result_server', type=str, default='localhost:9092', help='Kafka broker IP and port for sending results')
    parser.add_argument('--result_topic', type=str, default="capstone_drowsiness_output", help='Kafka topic for sending results of image inspection')
    parser.add_argument('--remote', type=bool, default=True, help='Flag for downloading YOLO model from local or remote (Azure Blob Storage)')
    parser.add_argument('--save_images', type=bool, default=False, help='Flag to save images to local with eyes recognition boxes and classes')
    parser.add_argument('--main', type=bool, default=False, help='Flag to save and load model on right directory if script is runned via main.py')    
    opt = parser.parse_known_args()[0] if known else parser.parse_args()
    return opt

def main(opt):

    # CREATE KAFKA CONSUMER WITH TOPIC, SERVER, ID AND CONSUMER GROUP
    consumer = Consumer(opt.topic, opt.server, opt.id, opt.group)
    # MAIN FUNCTION TO CONNECT TO A TOPIC AND CONSUME IMAGES FROM THAT TOPIC TOPIC. ONCE THIS IMAGES ARE PROCESSED, 
    # RESULTS ARE SENT TO A FINAL CONSUMER, SO IP, PORT AND TOPIC ARE PASSED AS ARG
    consumer.consume_camera(opt.result_server, opt.result_topic, opt.remote, opt.save_images, opt.main)

if __name__ == '__main__':
    
    opt = parse_opt()
    main(opt)