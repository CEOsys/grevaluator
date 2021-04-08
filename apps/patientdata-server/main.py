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
    data["patients"] = pd.read_pickle(BASE_PATH / "sample_data_shuffle_large.pkl.gz")


@app.get("/")
async def root():
    return {"message": "Patient Data Server"}


@app.get("/patients/list")
async def get_patient_list():
    df = data["patients"]
    variable_names = ["ward", "birth_date", "admission_hospitalisation"]

    return (
        df[df["variable_name"].isin(variable_names)].fillna("").to_dict(orient="list")
    )


@app.post("/patients/")
async def get_data(variable_name: List[str]):
    df = data["patients"]

    return df[df["variable_name"].isin(variable_name)].fillna("").to_dict(orient="list")


@app.post("/patient/{patient_id}")
async def get_patient_data(variable_name: List[str]):
    df = data["patients"].query("pseudo_fallnr=@patient_id")

    return df[df["variable_name"].isin(variable_name)].fillna("").to_dict(orient="list")
