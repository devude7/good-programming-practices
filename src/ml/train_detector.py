from pathlib import Path
from ultralytics import YOLO


DATA_YAML = "data/yolo/data.yaml"   
BASE_MODEL = "yolo11s.pt"          
IMG_SIZE = 960
EPOCHS = 60
BATCH = 16
DEVICE = "0"                        
WORKERS = 4                         
SEED = 42

PROJECT_DIR = "runs/detect"
RUN_NAME = "plate_yolov8n"


PATIENCE = 20 
COS_LR = True


def main() -> None:
    data_path = Path(DATA_YAML)
    if not data_path.exists():
        raise FileNotFoundError(f"data.yaml not found: {data_path.resolve()}")

    model = YOLO(BASE_MODEL)

    model.train(
        data=str(data_path),
        imgsz=IMG_SIZE,
        epochs=EPOCHS,
        batch=BATCH,
        device=DEVICE,
        workers=WORKERS,
        seed=SEED,
        project=PROJECT_DIR,
        name=RUN_NAME,
        patience=PATIENCE,
        cos_lr=COS_LR,
        verbose=True,
    )

    run_dir = Path(PROJECT_DIR) / RUN_NAME
    best = run_dir / "weights" / "best.pt"
    last = run_dir / "weights" / "last.pt"

    print(f"Run dir: {run_dir.resolve()}")
    print(f"Best weights: {best.resolve()} ({'OK' if best.exists() else 'MISSING'})")
    print(f"Last weights: {last.resolve()} ({'OK' if last.exists() else 'MISSING'})")


if __name__ == "__main__":
    main()
