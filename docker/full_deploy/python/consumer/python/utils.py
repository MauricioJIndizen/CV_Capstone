import cv2

def load_haarcascade():
    face_cascade_name = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    eye_cascade_name = cv2.data.haarcascades + 'haarcascade_eye.xml'
    
    face_cascade = cv2.CascadeClassifier()
    if not face_cascade.load(cv2.samples.findFile(face_cascade_name)):
        print("Error loading xml file")
        exit(0)

    eye_cascade = cv2.CascadeClassifier()
    if not eye_cascade.load(cv2.samples.findFile(eye_cascade_name)):
        print("Error loading xml file")
        exit(0)
        
    return face_cascade, eye_cascade