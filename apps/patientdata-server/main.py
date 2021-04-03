from typing import List
import os
from pathlib import Path
from fastapi import FastAPI
import pandas as pd

BASE_PATH = Path(os.getenv("CEOSYS_BASE_PATH")) / "data"  # type: ignore

data = {}
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    data["patients"] = pd.read_csv(BASE_PATH / "sample_data_shuffle.csv.gz")


@app.get("/")
async def root():
    return {"message": "Patient Data Server"}


@app.post("/patient/")
async def get_data(variable_name: List[str]):
    df = data["patients"]

    return df[df["variable_name"].isin(variable_name)].fillna("").to_dict(orient="list")
