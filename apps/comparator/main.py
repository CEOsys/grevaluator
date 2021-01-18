import os
from typing import Dict, List

import requests
from pathlib import Path
import pandas as pd
from fastapi import FastAPI
from comparator.comparator import process_guideline
from comparator.quantity import Quantity


app = FastAPI()
GUIDELINE_SERVER: str = os.environ["GUIDELINE_SERVER"]
PATIENTDATA_SERVER: str = os.environ["PATIENTDATA_SERVER"]
DATA_PATH: str = os.environ["CEOSYS_DATA_PATH"]


@app.get("/")
async def root() -> Dict:
    return {"message": "Comparator"}


def save_results(res, variable_names, guideline_id):
    summary = res[
        [("valid_exposure", ""), ("valid_population", ""), ("valid_treatment", "")]
    ].droplevel(level=1, axis=1)

    s_variable_names = pd.Series(
        {k: list(v) for k, v in variable_names.items()}, name="variable_name"
    ).rename_axis(index="type")
    s_variable_names = s_variable_names.explode().to_frame().reset_index()

    variable_names = [v for v in variable_names if v in res]

    details = res[variable_names].stack("variable_name").reset_index("variable_name")

    summary.to_pickle(Path(DATA_PATH) / f"guideline_{guideline_id}_results_summary.pkl")
    details.to_pickle(Path(DATA_PATH) / f"guideline_{guideline_id}_results_detail.pkl")
    s_variable_names.to_pickle(
        Path(DATA_PATH) / f"guideline_{guideline_id}_variable_names.pkl"
    )


def flatten(d: Dict[str, List[str]]) -> List[str]:
    """
    Flatten a dict of lists to a list

    Args:
        d: dict of lists

    Returns: flattened list

    """
    return list(set().union(*d.values()))


@app.get("/run")
async def run() -> str:
    guideline_ids = get_guideline_ids()

    for guideline_id in guideline_ids:
        guideline = get_guideline(guideline_id)
        variable_names, q_population, q_exposure = process_guideline(guideline)
        data = request_data(flatten(variable_names))
        res = compare(data, q_population, q_exposure)
        save_results(res, variable_names, guideline_id)

    return "Success"


def get_guideline_ids() -> List:
    r = requests.get(GUIDELINE_SERVER + "/guideline/list")
    return [gl["id"] for gl in r.json()]


def get_guideline(guideline_id: str) -> Dict:
    r_guideline = requests.get(GUIDELINE_SERVER + f"/guideline/get/{guideline_id}")
    guideline = r_guideline.json()

    return guideline


def request_data(variables: List[str]) -> pd.DataFrame:
    r = requests.post(PATIENTDATA_SERVER + "/patients/", json=variables)

    df = pd.DataFrame(r.json())
    df = (
        df.sort_values(by="datetime").groupby(["pseudo_fallnr", "variable_name"]).nth(0)
    )
    df = df.unstack("variable_name")
    df = df.swaplevel(axis=1).sort_index(axis=1)

    return df


def validate(df, quantity_groups, type_name):
    if type_name not in ["population", "exposure"]:
        raise ValueError(f'Invalid type_name "{type_name}"')

    col_names_group = []
    for group_name, quantities in quantity_groups.items():
        col_names_variables = []
        for q in quantities:
            if q.variable_name not in df.columns:
                continue

            col_name = (q.variable_name, f"valid_{type_name}")
            df[col_name] = df[(q.variable_name, "value")].apply(q.valid)
            col_names_variables.append(col_name)

        col_name = (f"valid_{type_name}", group_name)
        df[col_name] = df[col_names_variables].all(axis=1)
        col_names_group.append(col_name)

    df[(f"valid_{type_name}", "")] = df[col_names_group].any(axis=1)

    return df


def compare(
    df: pd.DataFrame,
    q_populations: Dict[str, List[Quantity]],
    q_exposures: Dict[str, List[Quantity]],
) -> pd.DataFrame:

    df = validate(df, q_populations, "population")
    df = validate(df, q_exposures, "exposure")

    df["valid_treatment"] = (
        df[("valid_population", "")] & df[("valid_exposure", "")]
    ) | (~df[("valid_population", "")])

    df = df.sort_index(axis=1)

    return df
