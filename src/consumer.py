import sqlite3
import time
from datetime import datetime

DB_FILE = "database/queue.db"

CHECK_INTERVAL_SECONDS = 5
JOB_DURATION_SECONDS = 30

def take_pending_job():
    conn = sqlite3.connect(DB_FILE, timeout=30, isolation_level=None)
    c = conn.cursor()

    try:
        c.execute("BEGIN IMMEDIATE")  

        c.execute("""
            SELECT id, description FROM jobs
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT 1
        """)
        row = c.fetchone()

        if row is None:
            conn.commit()
            conn.close()
            return None

        job_id, desc = row

        c.execute("""
            UPDATE jobs
            SET status='in_progress', started_at=?
            WHERE id=?
        """, (datetime.now().isoformat(timespec="seconds"), job_id))

        conn.commit()
        conn.close()

        return {"id": job_id, "description": desc}

    except sqlite3.OperationalError:
        return None

def mark_job_done(job_id: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        UPDATE jobs
        SET status='done', finished_at=?
        WHERE id=?
    """, (datetime.now().isoformat(timespec="seconds"), job_id))

    conn.commit()
    conn.close()

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
            print(f"[{datetime.now().isoformat(timespec='seconds')}] Brak zadań, czekam {CHECK_INTERVAL_SECONDS}s.")
            time.sleep(CHECK_INTERVAL_SECONDS)
        else:
            process_job(job)

if __name__ == "__main__":
    main()
