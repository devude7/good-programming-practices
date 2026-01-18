import time
import requests

def test_full_pipeline():
    r = requests.post(
        "http://localhost:8001/analyze",
        json={
            "image_url": "https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/images/family_photo.png"
        },
    )
    assert r.status_code == 200

    for _ in range(10):
        time.sleep(1)
        results = requests.get("http://localhost:8000/results").json()
        if len(results) > 0:
            break

    assert len(results) > 0
