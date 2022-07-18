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
"""
Guideline Recommendation Adherence Evaluator Module - FastAPI interface
"""

import os
from typing import Dict, List, Set

import requests
from pathlib import Path
import pandas as pd
from fastapi import FastAPI
from cgr_adherence.quantity import Quantity
from cgr_adherence.evaluator import AdherenceEvaluator
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    FastAPI Settings for adherence evaluator
    """

    guideline_server: str
    patientdata_server: str
    ceosys_data_path: str


app = FastAPI()
settings = Settings()


@app.get("/")
async def root() -> Dict:
    """
    Server greeting.

    Returns: Server greeting.

    """
    return {"message": "Adherence evaluator"}


def save_results(
    res: pd.DataFrame, variable_names: Dict[str, Set[str]], recommendation_id: str
) -> None:
    """
    Save results of the guideline recommendations adherence check to a file (to be read by the ui backend).

    Args:
        res: Results of the guideline recommendation adherence check
        variable_names: Clinical variable names that were required to evaluate guideline recommendation adherence
        recommendation_id: Guideline recommendation identifier

    Returns: None

    """
    summary = res[
        [("valid_exposure", ""), ("valid_population", ""), ("valid_treatment", "")]
    ].droplevel(level=1, axis=1)

    s_variable_names = pd.Series(
        {k: list(v) for k, v in variable_names.items()}, name="variable_name"
    ).rename_axis(index="type")
    s_variable_names = s_variable_names.explode().to_frame().reset_index()

    variable_names_set = [v for v in variable_names if v in res]

    details = (
        res[variable_names_set].stack("variable_name").reset_index("variable_name")
    )

    summary.to_pickle(
        Path(settings.ceosys_data_path)
        / f"guideline_recommendation_{recommendation_id}_results_summary.pkl"
    )
    details.to_pickle(
        Path(settings.ceosys_data_path)
        / f"guideline_recommendation_{recommendation_id}_results_detail.pkl"
    )
    s_variable_names.to_pickle(
        Path(settings.ceosys_data_path)
        / f"guideline_recommendation_{recommendation_id}_variable_names.pkl"
    )


def flatten(d: Dict[str, Set[str]]) -> List[str]:
    """
    Flatten a dict of lists to a list

    Args:
        d: dict of lists

    Returns: flattened list

    """
    return list(set().union(*d.values()))  # type: ignore


@app.get("/run")
async def run() -> str:
    """
    Performs guideline recommendation adherence evaluation.

    For each guideline recommendation, the guideline is fetched from the guideline interface. Then, the
    AdherenceEvaluator package is used to

    - (1) identify the clinical variables that are required to perform the guideline recommendation adherence check
      are determined
    - (2) create Quantity objects to check the rules defined by the guideline recommendation

    Next, the required clinical variables are requested from the clinical data interface and the Quantity objects are
    applied to these datasets to determine guideline recommendation adherence.

    Returns: "Success"

    """
    recommendation_ids = get_recommendation_ids()

    for recommendation_id in recommendation_ids:
        rec = get_recommendation(recommendation_id)
        variable_names, q_population, q_exposure = AdherenceEvaluator(
            rec
        ).process_guideline_recommendation()
        data = request_data(flatten(variable_names))
        res = compare(data, q_population, q_exposure)
        save_results(res, variable_names, recommendation_id)

    return "Success"


def get_recommendation_ids() -> List[str]:
    """
    Get all available guideline recommendation identifier

    Returns: List of available guideline recommendation identifier

    """
    r = requests.get(settings.guideline_server + "/recommendation/list")
    return [rec["id"] for rec in r.json()]


def get_recommendation(recommendation_id: str) -> Dict:
    """
    Retrieve a specific guideline recommendation from the guideline interface.

    Args:
        recommendation_id: Guideline recommendation identifier

    Returns: Guideline recommendation in FHIR format (JSON)

    """
    r_recommendation = requests.get(
        settings.guideline_server + f"/recommendation/get/{recommendation_id}"
    )
    recommendation = r_recommendation.json()

    return recommendation


def request_data(variables: List[str]) -> pd.DataFrame:
    """
    Retrieve clinical data from the clinical data interface

    Args:
        variables: List of clinical variables that are to be retrieved

    Returns: DataFrame with clinical data

    """
    r = requests.post(settings.patientdata_server + "/patients/", json=variables)

    df = pd.DataFrame(r.json())
    df = (
        df.sort_values(by="datetime").groupby(["pseudo_fallnr", "variable_name"]).nth(0)
    )
    df = df.unstack("variable_name")
    df = df.swaplevel(axis=1).sort_index(axis=1)

    return df


def validate(
    df: pd.DataFrame, quantity_groups: Dict[str, List[Quantity]], type_name: str
) -> pd.DataFrame:
    """
    Evaluates guideline recommendation on clinical data for the population or exposure part of the recommendation.

    Args:
        df: Clinical data with all required variables
        quantity_groups: population or exposure Quantity objects that need to be evaluated on the data
        type_name: "population" or "exposure"

    Returns: DataFrame indicating for each quantity group and in total if the rules defined by the quantity group are
        fulfilled in the data (i.e. if the recommendation is applicable (for "population") or implemented (for
        "exposure")).

    """
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
    """
    Evaluates guideline recommendation on clinical data.

    Args:
        df: Clinical data with all required variables.
        q_populations: population Quantity objects that need to be evaluated on the data
        q_exposures: exposure Quantity objects that need to be evaluated on the data

    Returns: DataFrame indicating for each quantity group and in total if the rules defined by the quantity group are
        fulfilled in the data (i.e. if the recommendation is applicable and implemented).

    """

    df = validate(df, q_populations, "population")
    df = validate(df, q_exposures, "exposure")

    df["valid_treatment"] = (
        df[("valid_population", "")] & df[("valid_exposure", "")]
    ) | (~df[("valid_population", "")])

    df = df.sort_index(axis=1)

    return df
