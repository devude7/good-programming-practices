from __future__ import annotations
import aio_pika

RABBIT_URL = "amqp://guest:guest@localhost/"
QUEUE_NAME = "plate_jobs"

async def get_connection() -> aio_pika.RobustConnection:
    return await aio_pika.connect_robust(RABBIT_URL)

async def publish_message(payload_bytes: bytes) -> None:
    conn = await get_connection()
    async with conn:
        channel = await conn.channel()
        await channel.declare_queue(QUEUE_NAME, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(body=payload_bytes, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=QUEUE_NAME,
        )
