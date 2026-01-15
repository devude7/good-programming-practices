from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
from .models import AnalysisJob

def create_job(db: Session, job_id: str, status: str = "queued") -> AnalysisJob:
    job = AnalysisJob(id=job_id, status=status)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def set_job_processing(db: Session, job_id: str) -> None:
    job = db.get(AnalysisJob, job_id)
    if job:
        job.status = "processing"
        db.commit()

def set_job_done(db: Session, job_id: str, *, plate_text: str, det_conf: float, ocr_conf: float, bbox_xyxy: list[int]) -> None:
    job = db.get(AnalysisJob, job_id)
    if job:
        job.status = "done"
        job.finished_at = datetime.utcnow()
        job.plate_text = plate_text
        job.det_conf = det_conf
        job.ocr_conf = ocr_conf
        job.bbox_xyxy = bbox_xyxy
        db.commit()

def set_job_failed(db: Session, job_id: str, error: str) -> None:
    job = db.get(AnalysisJob, job_id)
    if job:
        job.status = "failed"
        job.finished_at = datetime.utcnow()
        job.error = error
        db.commit()
