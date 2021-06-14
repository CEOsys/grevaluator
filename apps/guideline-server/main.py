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

import os
import re
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
import json
from fhir.resources.bundle import Bundle
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BASE_PATH = Path(os.environ["CEOSYS_BASE_PATH"], ".") / "FHIR"


class GuidelineException(Exception):
    pass


class GuidelineNotFoundException(GuidelineException):
    pass


class GuidelineLoginException(GuidelineException):
    pass


@app.get("/")
async def root():
    return {"message": "Guideline Server"}


def get_file_list(path, pattern):
    res = [os.path.join(path, f) for f in os.listdir(path) if re.search(pattern, f)]
    return res


def get_guideline_from_server(guideline_id: int):
    def get_login_token():
        auth = {
            "email": os.environ["MAGICAPP_EMAIL"],
            "password": os.environ["MAGICAPP_PASSWORD"],
        }
        url = os.environ["MAGICAPP_SERVER"] + "/auth/login"
        r = requests.post(url, data=auth)

        if r.status_code != 200:
            msg = "Could not login"
            if "error" in r.json():
                msg += f' ({r.json["error"]})'
            GuidelineLoginException(msg)

        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        return headers

    auth_header = get_login_token()
    r = requests.get(
        os.environ["MAGICAPP_SERVER"]
        + f"/api/v1/recommendations/{guideline_id}/rational",
        headers=auth_header,
    )
    m = re.match(
        r"recommendations-ceosys-api:[^\{]+({.*})", r.json()["text"], re.MULTILINE
    )

    if not m:
        raise GuidelineNotFoundException("Guideline pattern not matched")

    try:
        guideline = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise GuidelineNotFoundException("Could not decode guideline") from e

    return guideline


def get_guideline_from_file(guideline_id: int):
    fname = BASE_PATH / f"Recommendation_MA{guideline_id}.fhir.json"

    if not os.path.exists(fname):
        raise GuidelineNotFoundException(f'Guideline "{fname}" not found')

    with open(fname) as f:
        guideline = json.load(f)

    return guideline


def get_guideline(guideline_id: int):
    if os.environ["MAGICAPP_USE"] == 1:
        try:
            print(f"Reading guideline {guideline_id} from MAGICapp server")
            guideline = get_guideline_from_server(guideline_id)
            print("Read guideline from server")
            return guideline
        except GuidelineException as e:
            print(
                f"Guideline {guideline_id} not found on server ({str(e)}), falling back to local file"
            )
            pass
    else:
        print(f"Reading guideline {guideline_id} from local storage")

    try:
        return get_guideline_from_file(guideline_id)
    except GuidelineException as e:
        print(f"Guideline {guideline_id} not found locally ({str(e)}")

    raise GuidelineNotFoundException()


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
    try:
        guideline = get_guideline(guideline_id)
    except GuidelineException as e:
        raise HTTPException(status_code=404, detail=f"Guideline not found ({str(e)}")

    return guideline
