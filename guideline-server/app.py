import os
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

BASE_PATH = Path(os.getenv("CEOSYS_BASE_PATH")) / "FHIR"  # type: ignore


@app.get("/")
async def root():
    return {"message": "Guideline Server"}


def get_file_list(path, pattern):
    res = [f for f in os.listdir(path) if re.search(pattern, f)]
    return res


@app.get("/guideline/list")
async def list_guidelines():
    pattern = r"Recommendation_MA(\d+)\.fhir\.json$"

    return [
        re.search(pattern, fname).group(1)
        for fname in get_file_list(BASE_PATH, pattern)
    ]


@app.get("/guideline/get/{guideline_id}")
async def read_guideline(guideline_id: int):
    fname = BASE_PATH / f"Recommendation_MA{guideline_id}.fhir.json"

    if not os.path.exists(fname):
        raise HTTPException(status_code=404, detail="Guideline not found")
    with open(fname) as f:
        guideline = json.load(f)
    return guideline
