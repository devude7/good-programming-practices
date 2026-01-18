from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from typing import List

app = FastAPI()

class Result(BaseModel):
    image_url: str
    people_count: int

results: List[Result] = []  

@app.post("/results")
def save_result(result: Result):
    if int(time.time()) % 10 < 3:
        raise HTTPException(status_code=503, detail="Temporary unavailable")

    results.append(result)
    print(f"[SERVICE A] Saved: {result}")
    return {"status": "ok"}

@app.get("/results")
def get_results():
    return results
