import json
import pika
import requests
import time
from ai import detect_people

RABBIT_HOST = "rabbitmq"

def connect_rabbit():
    while True:
        try:
            print("[*] Connecting to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
            print("[✓] Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("[!] RabbitMQ not ready, retrying in 3s...")
            time.sleep(3)

connection = connect_rabbit()
channel = connection.channel()

channel.queue_declare(queue="image_tasks", durable=True)
channel.basic_qos(prefetch_count=1)

def callback(ch, method, properties, body):
    task = json.loads(body)
    url = task["image_url"]

    try:
        count = detect_people(url)

        payload = {
            "image_url": url,
            "people_count": count
        }

        response = requests.post(
            "http://service-a:8000/results",
            json=payload,
            timeout=5
        )

        if response.status_code != 200:
            raise Exception("Service A unavailable")

        print(f"[✓] Sent result: {payload}")
        ch.basic_ack(method.delivery_tag)

    except Exception as e:
        print(f"[!] Error, retry later: {e}")
        ch.basic_nack(method.delivery_tag, requeue=True)

channel.basic_consume(queue="image_tasks", on_message_callback=callback)

print("[*] Waiting for tasks...")
channel.start_consuming()
