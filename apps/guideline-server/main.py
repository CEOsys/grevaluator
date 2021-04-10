import os
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
import json
from fhir.resources.bundle import Bundle

app = FastAPI()

BASE_PATH = Path(os.environ["CEOSYS_BASE_PATH"], ".") / "FHIR"


@app.get("/")
async def root():
    return {"message": "Guideline Server"}


def get_file_list(path, pattern):
    res = [os.path.join(path, f) for f in os.listdir(path) if re.search(pattern, f)]
    return res


@app.get("/guideline/list")
async def list_guidelines():
    pattern = r"Recommendation_MA(\d+)\.fhir\.json$"

    guidelines = []

    for fname in get_file_list(BASE_PATH, pattern):
        id = re.search(pattern, fname).group(1)
        bundle = Bundle.parse_file(fname)
        title = bundle.entry[0].resource.title
        text = bundle.entry[0].resource.text.div

        guidelines.append({"id": id, "title": title, "text": text})

    return guidelines


@app.get("/guideline/get/{guideline_id}")
async def read_guideline(guideline_id: int):
    fname = BASE_PATH / f"Recommendation_MA{guideline_id}.fhir.json"

    if not os.path.exists(fname):
        raise HTTPException(status_code=404, detail="Guideline not found")
    with open(fname) as f:
        guideline = json.load(f)
    return guideline
