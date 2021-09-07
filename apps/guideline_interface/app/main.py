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
Guideline Interface - FastAPI interface
"""

import os
import re
from typing import List, Dict, Union

import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
import json
from fhir.resources.bundle import Bundle
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
BASE_PATH = Path(os.environ["CEOSYS_BASE_PATH"], ".") / "FHIR"


class GuidelineException(Exception):
    """
    Guideline exception base class
    """

    pass


class RecommendationNotFoundException(GuidelineException):
    """
    Guideline not found exception
    """

    pass


class GuidelineServerLoginException(GuidelineException):
    """
    Guideline server login exception
    """

    pass


def get_file_list(path: Union[str, Path], pattern: str) -> List[str]:
    """
    Returns all files in a paths that match a pattern.

    Args:
        path: Search path
        pattern: File name pattern

    Returns: List of all files that match the pattern.

    """
    res = [os.path.join(path, f) for f in os.listdir(path) if re.search(pattern, f)]
    return res


def get_guideline_recommendation_from_magicapp(recommendation_id: int) -> Dict:
    """
    Retrieve a guideline recommendation from MAGICapp server (https://app.magicapp.org/) by its identifier.

    For the time being, guideline recommendations are saved in the "rational" field of the MAGICapp interface, as
    currently no specific field for machine-readable versions of the guidelines exists in MAGICapp.

    Args:
        recommendation_id: Guideline recommendation identifier

    Returns: Guideline recommendation in FHIR format

    """

    def get_login_token() -> Dict:
        """
        Get login token for MAGICapp server.

        Returns: Authorization header to be used in requests.

        """
        auth = {
            "email": os.environ["MAGICAPP_EMAIL"],
            "password": os.environ["MAGICAPP_PASSWORD"],
        }
        url = os.environ["MAGICAPP_SERVER"] + "/auth/login"
        r = requests.post(url, data=auth)

        if r.status_code != 200:
            msg = "Could not login"
            if "error" in r.json():
                msg += f' ({r.json()["error"]})'
            GuidelineServerLoginException(msg)

        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        return headers

    auth_header = get_login_token()
    r = requests.get(
        os.environ["MAGICAPP_SERVER"]
        + f"/api/v1/recommendations/{recommendation_id}/rational",
        headers=auth_header,
    )
    m = re.match(
        r"recommendations-ceosys-api:[^\{]+({.*})", r.json()["text"], re.MULTILINE
    )

    if not m:
        raise RecommendationNotFoundException(
            "Guideline recommendation pattern not matched"
        )

    try:
        guideline = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise RecommendationNotFoundException(
            "Could not decode guideline recommendation"
        ) from e

    return guideline


def get_guideline_recommendation_from_file(recommendation_id: int) -> Dict:
    """
    Retrieve a guideline recommendation from local storage by its identifier

    Args:
        recommendation_id: Guideline recommendation identifier

    Returns: Guideline recommendation in FHIR format

    """
    fname = BASE_PATH / f"Recommendation_MA{recommendation_id}.fhir.json"

    if not os.path.exists(fname):
        raise RecommendationNotFoundException(f'Guideline "{fname}" not found')

    with open(fname) as f:
        guideline = json.load(f)

    return guideline


def get_guideline_recommendation(recommendation_id: int) -> Dict:
    """
    Retrieve a guideline recommendation by its identifier.

    Guidelines recommendations are fetched from the MAGICapp server and as a fallback option from local storage.

    Args:
        recommendation_id: Guideline recommendation identifier

    Returns: Guideline recommendation in FHIR format

    """
    if os.environ["MAGICAPP_USE"] == 1:
        try:
            print(
                f"Reading guideline recommendation {recommendation_id} from MAGICapp server"
            )
            guideline = get_guideline_recommendation_from_magicapp(recommendation_id)
            print("Read guideline from server")
            return guideline
        except GuidelineException as e:
            print(
                f"Guideline recommendation {recommendation_id} not found on server ({str(e)}), "
                f"falling back to local file"
            )
            pass
    else:
        print(
            f"Reading guideline recommendation {recommendation_id} from local storage"
        )

    try:
        return get_guideline_recommendation_from_file(recommendation_id)
    except GuidelineException as e:
        print(
            f"Guideline recommendation {recommendation_id} not found locally ({str(e)}"
        )

    raise RecommendationNotFoundException()


@app.get("/")
async def root() -> Dict:
    """
    Server greeting.

    Returns: Server greeting.

    """
    return {"message": "Guideline Server"}


@app.get("/recommendation/list")
async def list_guidelines() -> List[Dict]:
    """
    Get a list of available guideline recommendations.

    Returns: List of available guideline recommendations

    """
    pattern = r"Recommendation_MA(\d+)\.fhir\.json$"

    guidelines = []

    for fname in get_file_list(BASE_PATH, pattern):
        id = re.search(pattern, fname).group(1)  # type: ignore
        bundle = Bundle.parse_file(fname)
        title = bundle.entry[0].resource.title
        text = bundle.entry[0].resource.text.div

        guidelines.append({"id": id, "title": title, "text": text})

    return guidelines


@app.get("/recommendation/get/{recommendation_id}")
async def read_guideline(recommendation_id: int) -> Dict:
    """
    Get a specific guideline recommendation

    Args:
        recommendation_id: Guideline recommendation identifier

    Returns: Guideline recommendation in FHIR format

    """
    try:
        guideline = get_guideline_recommendation(recommendation_id)
    except GuidelineException as e:
        raise HTTPException(
            status_code=404, detail=f"Guideline recommendation not found ({str(e)}"
        )

    return guideline
