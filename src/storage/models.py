from __future__ import annotations
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from src.storage.db import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, index=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    det_conf = Column(Float, nullable=True)
    ocr_conf = Column(Float, nullable=True)
    plate_text = Column(String, nullable=True)

    bbox_xyxy = Column(JSON, nullable=True)   
    error = Column(String, nullable=True)
