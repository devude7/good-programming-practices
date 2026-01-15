from __future__ import annotations
import cv2
import numpy as np
from .detector import PlateDetector

detector = PlateDetector() 

def analyze_image_bytes(image_bytes: bytes):
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    out = detector.detect_and_ocr(img)

    if not out.success or out.detection is None:
        return {
            "success": False,
            "error": out.error or "analysis_failed",
        }

    d = out.detection
    return {
        "success": True,
        "bbox_xyxy": list(d.bbox_xyxy),
        "det_conf": float(d.confidence),
        "plate_text": d.ocr.best_text_norm,
        "ocr_conf": float(d.ocr.best_confidence),
    }
