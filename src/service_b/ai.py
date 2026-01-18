import cv2
import numpy as np
import requests

MODEL = "model/efficientdet-d0.pb"
CONFIG = "model/efficientdet-d0.pbtxt"

cvNet = cv2.dnn.readNetFromTensorflow(MODEL, CONFIG)
PERSON_CLASS_ID = 1

def detect_people(image_url: str) -> int:
    response = requests.get(image_url, timeout=10)
    image = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    blob = cv2.dnn.blobFromImage(image, size=(640, 640), swapRB=True)
    cvNet.setInput(blob)
    detections = cvNet.forward()

    count = 0
    for d in detections[0, 0]:
        if d[2] > 0.5 and int(d[1]) == PERSON_CLASS_ID:
            count += 1
    return count
