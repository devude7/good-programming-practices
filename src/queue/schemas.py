from __future__ import annotations
from pydantic import BaseModel

class EnqueueMessage(BaseModel):
    job_id: str
    image_b64: str  
    filename: str | None = None
