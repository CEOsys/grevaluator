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
User Interface Backend - FastAPI interface
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
import pandas as pd
import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, BaseSettings
from config import settings
import yaml


class Token(BaseModel):
    """
    Token for accessing the UI backend service after user authentication.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Additional data for user access token
    """

    username: Optional[str] = None


class User(BaseModel):
    """
    Website user for authentication
    """

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """
    User in database
    """

    hashed_password: str


def load_user_db() -> Dict:
    """
    Read the user database from yaml file

    Returns: User database as dictionary

    """
    with open(os.path.dirname(__file__) + "/auth/users_db.yml") as f:
        content = yaml.load(f, Loader=yaml.SafeLoader)
    return content


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
user_db = load_user_db()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify user provided password against hashed database password.

    Args:
        plain_password: User provided plaintext password
        hashed_password: Hashed password from user database.

    Returns: True if passwords match, False otherwise

    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash plaintext password.

    Args:
        password: Plaintext password

    Returns: Hashed password

    """
    return pwd_context.hash(password)


def get_user(db: Dict, username: str) -> Optional[User]:
    """
    Retrieve a user from the user database

    Args:
        db: User database
        username: Username

    Returns: User entry from user database

    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(db: Dict, username: str, password: str) -> Union[bool, User]:
    """
    Retrieve a user from the user database using username and password.

    Args:
        db: User database
        username: Username
        password: Plaintext password

    Returns: User object if username exists and password is correct, false otherwise

    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token for user authentication-

    Args:
        data: Data encoded by the token
        expires_delta: timedelta object specifying the expiration time (default: 15 minutes)

    Returns: Access token

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Retrieve user from database by access token.

    Args:
        token: Access token provided by user

    Returns: User if access token is valid.

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(user_db, username=token_data.username)  # type:ignore
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure current user is active (non-disabled)

    Args:
        current_user: Current user

    Returns: current_user if user is not disabled

    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Dict:
    """
    Login form to retrieve access token.

    Args:
        form_data: Formulat data with "username" and "password" fields.

    Returns: Access token if the provided username and password are valid.

    """
    user = authenticate_user(user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires  # type: ignore  # (already established that user is not bool False)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def root() -> Dict:
    """
    Server greeting.

    Returns: Server greeting.

    """
    return {"message": "UI Backend Server"}


def get_recommendation_results_summary(recommendation_id: str) -> pd.DataFrame:
    """
    Retrieves the summary of the guideline recommendation compliance evaluation.

    The summary includes patient identifier, ward, birth date, time on ICU and whether the guideline recommendation
    is applicable and implemented.

    Args:
        recommendation_id: Guideline recommendation identifier.

    Returns: Summary of the guideline recommendation compliance evaluation

    """
    try:
        r = (
            pd.read_pickle(
                Path(settings.ceosys_data_path)
                / f"guideline_recommendation_{recommendation_id}_results_summary.pkl"
            )
            .fillna("nan")
            .reset_index()
        )
    except FileNotFoundError:
        raise HTTPException(404, "Guideline recommendation not found")
    return r


def get_recommendation_results_details(recommendation_id: str) -> pd.DataFrame:
    """
    Retrieves the details of the guideline recommendation compliance evaluation.

    The detailed results include all clinical data that was used to evaluated the guideline recommendation compliance.

    Args:
        recommendation_id: Guideline recommendation identifier.

    Returns: Details of the guideline recommendation compliance evaluation.

    """
    try:
        r = (
            pd.read_pickle(
                Path(settings.ceosys_data_path)
                / f"guideline_recommendation_{recommendation_id}_results_detail.pkl"
            )
            .fillna("nan")
            .reset_index()
        )
    except FileNotFoundError:
        raise HTTPException(404, "Guideline recommendation not found")
    return r


def get_recommendation_variables(recommendation_id: str) -> pd.DataFrame:
    """
    Retrieve the clinical variables names that are required to evaluate guideline recommendation compliance of the
    given recommendation.

    Args:
        recommendation_id: Guideline recommendation identifier.

    Returns: List of clinical variables names

    """
    try:
        r = pd.read_pickle(
            Path(settings.ceosys_data_path)
            / f"guideline_{recommendation_id}_variable_names.pkl"
        )
    except FileNotFoundError:
        raise HTTPException(404, "Guideline recommendation not found")
    return r


def get_recommendation_ids() -> Dict:
    """
    Retrieve all available guideline recommendation identifier from the guideline interface.

    Returns: List of available guideline recommendation identifier

    """
    r = requests.get(settings.guideline_server + "/recommendation/list")
    return r.json()


def get_patients_from_recommendation(recommendation_id: str) -> List:
    """
    Retrieve list of patients that were evaluated for a specific guideline recommendation.

    Args:
        recommendation_id: Guideline recommendation identifier.

    Returns: List of patients

    """
    ret = (
        get_recommendation_results_summary(recommendation_id)
        .reset_index()["pseudo_fallnr"]
        .unique()
    )
    return list(ret)


def request_patient_data(patient_id: str, variable_name: List[str]) -> pd.DataFrame:
    """
    Get clinical data for a specific patient.

    Args:
        patient_id: Patient identifier
        variable_name: List of clinical variable names to return for the patients.

    Returns: List of all available values for the requested variables for the specified patient.

    """
    r = requests.post(
        settings.patientdata_server + f"/patient/{patient_id}", json=variable_name
    )

    df = pd.DataFrame(r.json())

    return df


@app.get("/recommendation/list")
async def get_recommendation_list(
    current_user: User = Depends(get_current_active_user),
) -> Dict:
    """
    Lists identifiers of available guideline recommendations.

    Args:
        current_user: Authenticated user

    Returns: List of available guideline recommendation identifier

    """
    return get_recommendation_ids()


@app.get("/recommendation/variables/{recommendation_id}")
async def get_recommendation_variable_names(
    recommendation_id: str, current_user: User = Depends(get_current_active_user)
) -> Dict:
    """
    Lists clinical variable names required to evaluate a specific guideline recommendation.

    Args:
        recommendation_id: Guideline recommendation identifier.
        current_user: Authenticated user

    Returns: Clinical variable names

    """
    return get_recommendation_variables(recommendation_id).to_dict(orient="records")


@app.get("/recommendation/get/{recommendation_id}")
async def get_recommendation_results(
    recommendation_id: str, current_user: User = Depends(get_current_active_user)
) -> Dict:
    """
    Get results (summary + detailed) of the guideline recommendation evaluation on clinical data.

    Args:
        recommendation_id: Guideline recommendation identifier.
        current_user: Authenticated user

    Returns: Results (summary + detailed) of the guideline recommendation evaluation

    """
    df_summary = get_recommendation_results_summary(recommendation_id)
    df_detail = get_recommendation_results_details(recommendation_id)

    return {
        "summary": df_summary.to_dict(orient="records"),
        "detail": df_detail.to_dict(orient="records"),
    }


@app.get("/patients/list")
async def list_patients(current_user: User = Depends(get_current_active_user)) -> Dict:
    """
    List current patients

    Args:
        current_user: Authenticated user

    Returns: Current patients

    """
    r = requests.get(settings.patientdata_server + "/patients/list")
    df = pd.DataFrame(r.json())
    df = (
        df.sort_values(by=["pseudo_fallnr", "variable_name", "datetime"])
        .groupby(["pseudo_fallnr", "variable_name"])
        .nth(-1)["value"]
        .unstack("variable_name")
    )
    return df.reset_index().to_dict(orient="records")


@app.get("/patient/list/{recommendation_id}")
async def list_patient_by_recommendation(
    recommendation_id: str, current_user: User = Depends(get_current_active_user)
) -> List:
    """
    List current patients for a specific guideline recommendation.

    Args:
        recommendation_id: Guideline recommendation identifier.
        current_user: Authenticated user

    Returns: Current patients for specific guideline recommendation.

    """
    return get_patients_from_recommendation(recommendation_id)


@app.get("/patient/get")
async def get_patient_info(
    patient_id: str,
    recommendation_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Dict:
    """
    Get patient data of a specific patient

    Args:
        patient_id: Patient identifier
        recommendation_id: Guideline recommendation identifier.
        current_user: Authenticated user

    Returns: Patient data of a specific patient.

    """
    variables = list(
        get_recommendation_variables(recommendation_id)["variable_name"].unique()
    )
    df = request_patient_data(patient_id, variables)

    return df.to_dict(orient="records")
