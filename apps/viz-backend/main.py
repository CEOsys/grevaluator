from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

data = {}


@app.on_event("startup")
async def startup_event():
    data["patients"] = pd.read_csv("../../data/sample_data_shuffle.csv.gz")


@app.get("/")
async def root():
    return {"message": "Patient Viz Server"}


@app.get("/patient/list/")
async def list_patients():
    ret = data["patients"]["pseudo_fallnr"].unique()
    return list(ret)


@app.get("/patient/get/{fallnr}")
async def list_patient(fallnr: str):
    patient = data["patients"].query("pseudo_fallnr==@fallnr")

    if len(patient) == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient.fillna("").to_dict(orient="list")
