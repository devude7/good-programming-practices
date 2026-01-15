import json
import cv2
import numpy as np
import pika
import requests

MODEL = "model/efficientdet-d0.pb"
CONFIG = "model/efficientdet-d0.pbtxt"

cvNet = cv2.dnn.readNetFromTensorflow(MODEL, CONFIG)

PERSON_CLASS_ID = 1  

def detect_people(image_url: str) -> int:
    response = requests.get(image_url)
    image = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    rows, cols = image.shape[:2]

    blob = cv2.dnn.blobFromImage(image, size=(640, 640), swapRB=True, crop=False)
    cvNet.setInput(blob)

    cvOut = cvNet.forward()

    count = 0
    for detection in cvOut[0, 0, :, :]:
        score = float(detection[2])
        if score > 0.5:  
            class_id = int(detection[1])
            if class_id == PERSON_CLASS_ID:
                count += 1
                left = int(detection[3] * cols)
                top = int(detection[4] * rows)
                right = int(detection[5] * cols)
                bottom = int(detection[6] * rows)
                cv2.rectangle(image, (left, top), (right, bottom), (23, 230, 210), 2)
    return count

def callback(ch, method, properties, body):
    task = json.loads(body)
    url = task["image_url"]

    try:
        count = detect_people(url)
        print(f"[✓] Persons detected: {count} | {url}")
    except Exception as e:
        print(f"[!] Error: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="127.0.0.1", port=5672)
)
channel = connection.channel()
channel.queue_declare(queue="image_tasks", durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="image_tasks", on_message_callback=callback)

print("Waiting for tasks...")
channel.start_consuming()
