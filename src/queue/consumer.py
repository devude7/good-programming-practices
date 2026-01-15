from __future__ import annotations
import asyncio
import base64
import json
import traceback

import aio_pika
from sqlalchemy.orm import Session

from src.queue.rabbit import RABBIT_URL, QUEUE_NAME
from src.queue.schemas import EnqueueMessage
from src.storage.db import SessionLocal, Base, engine
from src.storage import crud
from src.ml.service import analyze_image_bytes

Base.metadata.create_all(bind=engine)


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    print("[worker] message received")

    try:
        async with message.process(requeue=False):
            print(f"[worker] raw bytes = {len(message.body)}")

            payload = json.loads(message.body.decode("utf-8"))
            msg = EnqueueMessage(**payload)

            print(f"[worker] job_id={msg.job_id}")

            db: Session = SessionLocal()
            try:
                crud.set_job_processing(db, msg.job_id)
                print(f"[worker] job {msg.job_id} -> processing")

                image_bytes = base64.b64decode(msg.image_b64)
                print(f"[worker] image bytes = {len(image_bytes)}")

                result = analyze_image_bytes(image_bytes)
                print(f"[worker] analyze result success={result.get('success')}")

                if not result["success"]:
                    crud.set_job_failed(
                        db,
                        msg.job_id,
                        result.get("error", "analysis_failed"),
                    )
                    print(f"[worker] job {msg.job_id} FAILED")
                    return

                crud.set_job_done(
                    db,
                    msg.job_id,
                    plate_text=result["plate_text"],
                    det_conf=result["det_conf"],
                    ocr_conf=result["ocr_conf"],
                    bbox_xyxy=result["bbox_xyxy"],
                )

                print(
                    f"[worker] job {msg.job_id} DONE | "
                    f"plate={result['plate_text']} "
                    f"det={result['det_conf']:.2f} "
                    f"ocr={result['ocr_conf']:.2f}"
                )

            finally:
                db.close()
                print(f"[worker] db closed for job {msg.job_id}")

    except Exception:
        print("[worker] EXCEPTION while processing message")
        traceback.print_exc()
        raise


async def main() -> None:
    print("[worker] starting consumer")
    print(f"[worker] RABBIT_URL={RABBIT_URL}")
    print(f"[worker] QUEUE_NAME={QUEUE_NAME}")

    conn = await aio_pika.connect_robust(RABBIT_URL)
    async with conn:
        channel = await conn.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        print("[worker] connected, waiting for messages...")
        await queue.consume(handle_message)

        print(f"[*] Waiting for messages in {QUEUE_NAME}. Ctrl+C to exit.")
        await asyncio.Future()  


if __name__ == "__main__":
    asyncio.run(main())
