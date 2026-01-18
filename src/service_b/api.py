import json
import pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ImageTask(BaseModel):
    image_url: str


def publish_task(task: dict):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq")
        )
        channel = connection.channel()
        channel.queue_declare(queue="image_tasks", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="image_tasks",
            body=json.dumps(task),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        connection.close()

    except Exception as e:
        print("RabbitMQ error:", e)
        raise HTTPException(status_code=503, detail="Queue unavailable")


@app.post("/analyze")
def analyze(task: ImageTask):
    publish_task(task.dict())
    return {"status": "queued"}
