import csv
import os
import time
from datetime import datetime

QUEUE_FILE = "database/queue.csv"
LOCK_FILE = "queue.lock"

CHECK_INTERVAL_SECONDS = 5
JOB_DURATION_SECONDS = 30

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

def load_jobs():
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_jobs(jobs):
    fieldnames = ["id", "status", "created_at", "started_at", "finished_at", "description"]
    with open(QUEUE_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)

def take_pending_job():
    acquire_lock()
    try:
        jobs = load_jobs()
        for job in jobs:
            if job["status"] == "pending":
                job["status"] = "in_progress"
                job["started_at"] = datetime.now().isoformat(timespec="seconds")
                job_id = job["id"]
                save_jobs(jobs)
                return job
        return None
    finally:
        release_lock()

def mark_job_done(job_id: str):
    acquire_lock()
    try:
        jobs = load_jobs()
        for job in jobs:
            if job["id"] == job_id:
                job["status"] = "done"
                job["finished_at"] = datetime.now().isoformat(timespec="seconds")
                break
        save_jobs(jobs)
    finally:
        release_lock()

def process_job(job):
    job_id = job["id"]
    desc = job["description"]
    print(f"[{datetime.now().isoformat(timespec='seconds')}] START pracy {job_id}: {desc}")
    time.sleep(JOB_DURATION_SECONDS)
    mark_job_done(job_id)
    print(f"[{datetime.now().isoformat(timespec='seconds')}] KONIEC pracy {job_id}: {desc}")

def main():
    print("Consumer uruchomiony. Czekam na zadania...")
    while True:
        job = take_pending_job()
        if job is None:
            print(f"[{datetime.now().isoformat(timespec='seconds')}] Brak zadań. Sprawdzę ponownie za {CHECK_INTERVAL_SECONDS}s.")
            time.sleep(CHECK_INTERVAL_SECONDS)
        else:
            process_job(job)

if __name__ == "__main__":
    main()
