import sqlite3
import uuid
from datetime import datetime
import argparse
import os

DB_FILE = "database/queue.db"

def init_db():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TEXT,
            started_at TEXT,
            finished_at TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_job(description: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    job_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat(timespec="seconds")

    c.execute("""
        INSERT INTO jobs (id, status, created_at, description)
        VALUES (?, 'pending', ?, ?)
    """, (job_id, created_at, description))

    conn.commit()
    conn.close()
    print(f"Dodano zadanie: {job_id} - {description}")

def main():
    parser = argparse.ArgumentParser(description="Producer - dodaje zadania do kolejki.")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--desc", type=str, default="Rozmowa telefoniczna")
    args = parser.parse_args()

    init_db()

    for i in range(1, args.count + 1):
        desc = f"{args.desc} #{i}"
        add_job(desc)

if __name__ == "__main__":
    main()
