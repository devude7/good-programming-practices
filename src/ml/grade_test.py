from __future__ import annotations

import random
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import cv2

from src.ml.detector import PlateDetector
from src.ml.ocr import normalize_plate_text
from src.eval.evaluate import calculate_final_grade

XML_PATH = Path("data/annotations.xml")
PHOTOS_DIR = Path("data/photos")

N_SAMPLES = 100
SEED = 30 

DEBUG = False
DEBUG_FAIL = True


@dataclass
class GTRecord:
    name: str
    bbox_xyxy: tuple[float, float, float, float]
    plate_text: str


def parse_cvat_xml(xml_path: Path) -> list[GTRecord]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    out: list[GTRecord] = []

    for img in root.findall(".//image"):
        name = img.attrib.get("name")
        if not name:
            continue

        for box in img.findall("./box"):
            if box.attrib.get("label") != "plate":
                continue

            xtl = float(box.attrib["xtl"])
            ytl = float(box.attrib["ytl"])
            xbr = float(box.attrib["xbr"])
            ybr = float(box.attrib["ybr"])

            plate_text = ""
            for attr in box.findall("./attribute"):
                if attr.attrib.get("name") == "plate number":
                    plate_text = (attr.text or "").strip()
                    break

            out.append(GTRecord(name=name, bbox_xyxy=(xtl, ytl, xbr, ybr), plate_text=plate_text))
            break

    return out


def iou_xyxy(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih

    a_area = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    b_area = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = a_area + b_area - inter

    return float(inter / denom) if denom > 0 else 0.0


def main() -> None:
    gt = parse_cvat_xml(XML_PATH)
    if not gt:
        raise SystemExit("No GT records parsed from annotations.xml")

    gt = [r for r in gt if (PHOTOS_DIR / r.name).exists()]
    if not gt:
        raise SystemExit("No GT images found in data/photos")

    random.seed(SEED)
    sample = random.sample(gt, k=min(N_SAMPLES, len(gt)))

    detector = PlateDetector(cut_left_ratio=0.1)

    correct = 0
    processed = 0
    detected = 0
    ocr_nonempty = 0

    iou_sum = 0.0

    t0 = time.perf_counter()

    for rec in sample:
        img_path = PHOTOS_DIR / rec.name
        img = cv2.imread(str(img_path))
        if img is None:
            continue

        if DEBUG:
            out = detector.debug_show(img, window_name=rec.name, ground_truth=rec.plate_text)
        elif DEBUG_FAIL:
            out = detector.debug_fail(img, sample_name=rec.name, ground_truth=rec.plate_text)
        else:
            out = detector.detect_and_ocr(img)

        processed += 1

        gt_text_norm = normalize_plate_text(rec.plate_text)

        if out.success and out.detection is not None:
            detected += 1
            pred_bbox = out.detection.bbox_xyxy
            iou_sum += iou_xyxy(rec.bbox_xyxy, pred_bbox)

            pred_text_norm = out.detection.ocr.best_text_norm
            if pred_text_norm:
                ocr_nonempty += 1

            if pred_text_norm == gt_text_norm and gt_text_norm != "":
                correct += 1

    t1 = time.perf_counter()
    total_time = t1 - t0

    if processed == 0:
        raise SystemExit("Processed 0 images")

    accuracy_percent = 100.0 * (correct / processed)
    mean_iou = iou_sum / processed

    print(f"Images available: {len(gt)}")
    print(f"Sampled: {len(sample)} | Processed: {processed}")
    print(f"Detected: {detected}/{processed} | OCR non-empty: {ocr_nonempty}/{processed}")
    print(f"Accuracy: {accuracy_percent:.2f}% ({correct}/{processed})")
    print(f"IoU: {mean_iou:.4f} ({processed} images)")
    print(f"Time for {processed} images: {total_time:.3f}s")
    if processed != 100:
        print(f"Estimated time for 100 images: {total_time * (100.0 / processed):.3f}s")

    grade = calculate_final_grade(
        accuracy_percent,
        total_time if processed == 100 else total_time * (100.0 / processed),
    )
    print("Final grade:", grade)


if __name__ == "__main__":
    main()
