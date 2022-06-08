import os
import ctypes
import time
import docker

from typing import Optional


def is_container_running(container_name: str) -> Optional[bool]:
    
    while(True):
        
        try:
            cli = docker.APIClient()
            inspect_dict = cli.inspect_container('capstone_drowsiness_kafka_server')
            state = inspect_dict['State']
            
            is_running = state['Status'] == 'running'
            
            if is_running:
                break
        except Exception as e:
            time.sleep(5)

def out_header(string):
    print(string)

def clean_up(string):

    ctypes.windll.kernel32.SetConsoleTitleW("Capstone_Drowsiness")   

    out_header('Cleanup')
    os.system('docker system prune')
    os.system('docker rmi wurstmeister/kafka')
    os.system('docker rmi wurstmeister/zookeeper')
    os.system('docker system prune')
    os.system('docker volume prune')
    out_header(string)

if __name__ == "__main__":

    #    

    launch_title = 'Start up'
    kafka_server_container_name = 'capstone_drowsiness_kafka_server'

    #

    clean_up(launch_title)
    
    # Kafka-Server #
    os.system('start "Docker Kafka Server" cmd /k "docker-compose -f docker-compose.yml up"')
    
    is_container_running(kafka_server_container_name)
    
    out_header('Kafka Server Running')
    
    # Kafka-Producer #
    #os.system('start "Docker Producer" cmd /k "docker build -t producer python/producer/. && docker run -it producer"')
    
    os.system('start "Kafka Producer" cmd /k "python python/producer/python/producer_main.py"')
    
    # Kafka-Consumer #
    
    os.system('start "Kafka Consumer" cmd /k "python python/consumer/python/consumer_main.py"')
    #os.system('start "Docker Consumer" cmd /k "docker build -t consumer python/consumer/. && docker run -it consumer"')