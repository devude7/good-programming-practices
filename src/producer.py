import json
import pika
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "image_tasks"

class ImageRequest(BaseModel):
    image_url: str

def publish_task(data: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

@app.post("/analyze_img")
def analyze_image(req: ImageRequest):
    publish_task({"image_url": req.image_url})
    return {"status": "queued"}
