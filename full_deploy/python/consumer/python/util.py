import os
from azure.storage.blob import BlobServiceClient
from zipfile import ZipFile

def download_from_azure():
    # FUNCTION FOR DOWNLOADING YOLO MODEL AND WEIGHTS FROM AZURE BLOB STORAGE

    connect_str = "DefaultEndpointsProtocol=https;AccountName=d2mcapstones00;AccountKey=cHCeAzdLoZKhZi6d/wIzeDJMQJeWF3OsnbcuDgZtskgnsmEXYezGGnSBGGWd+J9hsyVIfDddjtXP+AStPlvNjA==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    test_containers = blob_service_client.list_containers()
    for element in test_containers:
        if "drowsiness" in element.name:
            container = element

    # LIST BLOBS IN CONTAINER AND GET YOLO MODEL AND WEIGHTS
    container_client = blob_service_client.get_container_client(container) 

    blob_list = container_client.list_blobs()
    for element in blob_list:
        if "yolov2.pt" in element.name:
            weights = element
        elif "ultralytics_yolov5_master" in element.name:
            model = element
            
    local_path = os.getcwd()
    directory = os.path.join(local_path, 'model', 'yolo')
    if os.path.isdir(directory) == False:
        os.makedirs(directory)

    # DOWNLOAD YOLO WEIGHTS
    download_weight_path = os.path.join(directory, weights.name)
    print("Downloading YOLO weights in " + download_weight_path)

    with open(download_weight_path, "wb") as download_file:
        download_file.write(container_client.download_blob(weights.name).readall())

    # DOWNLOAD YOLO MODEL (ZIP)
    download_model_path = os.path.join(directory, model.name)
    print("Downloading YOLO model in " + download_model_path)

    with open(download_model_path, "wb") as download_file:
        download_file.write(container_client.download_blob(model.name).readall())

    # UNZIP YOLO MODEL
    with ZipFile(download_model_path, 'r') as zipObj:
        zipObj.extractall(directory)


# CLASS FOR SORTING FINAL RESULTS
class sorted_list():
    
    def __init__(self, max_len, order_position):
        self.max_len = max_len
        self.order_position = order_position
        self.current_len = 0
        self.check_wait = 0
        self.max_check_wait = 5
        self.alert = False
        self.iter = 0
        
        self.list = []

    def start_alert(self, n):
        print('START ' + str(n))
    
    # FUNCTION FOR STOP ALERT
    def end_alert(self, n):
        print('END ' + str(n))

    # APPEND NEW RESULTS AND SORT THEM TO CHECK IN ORDER IF ANY IMAGE CONTAINE OPENED EYES  
    def append(self, value):
        self.iter += 1
        if self.current_len < self.max_len:
            self.current_len += 1
        else:
            self.list.pop(0)
            
        self.list.append(value)
        sorted(self.list, key=lambda x:x[1])

        self.check_wait += 1
        if self.check_wait == self.max_check_wait:
            self.check_wait = 0
            asleep = self.check_drowsy()
            if self.alert and not asleep:
                self.alert = False
                self.end_alert(self.iter)
            else:
                if not self.alert and asleep:
                    self.alert = True
                    self.start_alert(self.iter)

    # CHECK IF ANY OF 90 RESULTS IS OPENED EYE
    def check_drowsy(self):
        flag = True
        for x in self.list:
            if 'OPENED' in x[2]:
                flag = False
                break
        return flag
    
    def get_len(self):
        return len(self.list)

    # FUNCTION FOR START ALERT AFTER 90 FRAMES WITH CLOSED EYES
    