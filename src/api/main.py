from __future__ import annotations
import base64
import json
import uuid

from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.storage.db import Base, engine
from src.storage import crud
from src.queue.rabbit import publish_message
from src.queue.schemas import EnqueueMessage
from src.ml.service import analyze_image_bytes

from fastapi import HTTPException
from src.storage.models import AnalysisJob
import subprocess
import sys
from pathlib import Path


app = FastAPI(title="Plate API")
Base.metadata.create_all(bind=engine)

@app.post("/analyze")
async def analyze_now(file: UploadFile = File(...), db: Session = Depends(get_db)):
    image_bytes = await file.read()
    result = analyze_image_bytes(image_bytes)

    job_id = str(uuid.uuid4())
    crud.create_job(db, job_id, status="processing")

    if not result["success"]:
        crud.set_job_failed(db, job_id, result.get("error", "analysis_failed"))
        return {"job_id": job_id, **result}

    crud.set_job_done(
        db,
        job_id,
        plate_text=result["plate_text"],
        det_conf=result["det_conf"],
        ocr_conf=result["ocr_conf"],
        bbox_xyxy=result["bbox_xyxy"],
    )
    return {"job_id": job_id, **result}

@app.post("/enqueue")
async def enqueue(file: UploadFile = File(...), db: Session = Depends(get_db)):
    image_bytes = await file.read()
    job_id = str(uuid.uuid4())

    crud.create_job(db, job_id, status="queued")

    msg = EnqueueMessage(
        job_id=job_id,
        image_b64=base64.b64encode(image_bytes).decode("ascii"),
        filename=file.filename,
    )

    await publish_message(json.dumps(msg.model_dump()).encode("utf-8"))
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(AnalysisJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at,
        "finished_at": job.finished_at,
        "plate_text": job.plate_text,
        "det_conf": job.det_conf,
        "ocr_conf": job.ocr_conf,
        "bbox_xyxy": job.bbox_xyxy,
        "error": job.error,
    }


@app.post("/admin/run-grade-test")
def run_grade_test():
    script_path = Path("src/ml/grade_test.py")

    if not script_path.exists():
        raise HTTPException(status_code=500, detail="grade_test.py not found")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.ml.grade_test"],
            capture_output=True,
            text=True,
            timeout=300,  
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="grade_test timeout")

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
