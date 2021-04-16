#  This file is part of CEOsys Recommendation Checker.
#
#  Copyright (c) 2021 CEOsys project team <https://covid-evidenz.de>.
#
#  CEOsys Recommendation Checker is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  CEOsys Recommendation Checker is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with CEOsys Recommendation Checker.  If not, see <https://www.gnu.org/licenses/>.

from typing import List
import os
from pathlib import Path
from fastapi import FastAPI
import pandas as pd

BASE_PATH = Path(os.environ["CEOSYS_BASE_PATH"]) / "data"

data = {}
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    data["patients"] = pd.read_pickle(
        BASE_PATH / "sample_data_shuffle_large.pkl.gz"
    ).dropna(subset=["value"])


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
async def get_patient_data(patient_id: str, variable_name: List[str]):
    df = data["patients"]
    df = df[df["pseudo_fallnr"] == patient_id]

    return df[df["variable_name"].isin(variable_name)].fillna("").to_dict(orient="list")
