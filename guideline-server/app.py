import os
from fastapi import FastAPI, HTTPException
import json

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Guideline Server"}


@app.get("/guideline/{guideline_id}")
async def read_guideline(guideline_id: int):
    fname = f"../FHIR/Recommendation_MA{guideline_id}.fhir.json"

    if not os.path.exists(fname):
        raise HTTPException(status_code=404, detail="Guideline not found")
    with open(fname) as f:
        guideline = json.load(f)
    return guideline
