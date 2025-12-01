import csv
import os
import uuid
from datetime import datetime
import argparse
import time

QUEUE_FILE = "database/queue.csv"
LOCK_FILE = "queue.lock"

def acquire_lock(timeout=10, delay=0.1):
    start = time.time()
    while True:
        try:
            with open(LOCK_FILE, "x"):
                return
        except FileExistsError:
            if time.time() - start > timeout:
                raise TimeoutError("Nie udało się zdobyć locka na plik kolejki.")
            time.sleep(delay)

def release_lock():
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass

def init_queue_file_if_needed():
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "status", "created_at", "started_at", "finished_at", "description"])

def add_job(description: str):
    acquire_lock()
    try:
        init_queue_file_if_needed()
        job_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat(timespec="seconds")
        row = [job_id, "pending", created_at, "", "", description]

        with open(QUEUE_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print(f"Dodano zadanie: {job_id} - {description}")
    finally:
        release_lock()

def main():
    parser = argparse.ArgumentParser(description="Producer - dodaje zadania do kolejki.")
    parser.add_argument("--count", type=int, default=1, help="Ile zadań dodać do kolejki (domyślnie 1)")
    parser.add_argument("--desc", type=str, default="Rozmowa telefoniczna", help="Opis zadania")
    args = parser.parse_args()

    for i in range(1, args.count + 1):
        desc = f"{args.desc} #{i}"
        add_job(desc)

if __name__ == "__main__":
    main()
