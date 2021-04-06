import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from config import settings
import yaml

DATA_PATH = Path(os.getenv("CEOSYS_DATA_PATH"))  # type : ignore
GUIDELINE_SERVER = os.getenv("GUIDELINE_SERVER")
PATIENTDATA_SERVER = os.getenv("PATIENTDATA_SERVER")

data = {}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def load_user_db():
    with open(os.path.dirname(__file__) + "/auth/users_db.yml") as f:
        content = yaml.load(f, Loader=yaml.SafeLoader)
    return content


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_db = load_user_db()

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
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


async def get_current_user(token: str = Depends(oauth2_scheme)):
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


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/")
async def root():
    return {"message": "Patient Viz Server"}


def get_guideline_results_summary(guideline_id):
    try:
        r = pd.read_pickle(
            DATA_PATH / f"guideline_{guideline_id}_results_summary.pkl"
        ).fillna("nan")
    except FileNotFoundError:
        raise HTTPException(404, "Guideline not found")
    return r


def get_guideline_results_details(guideline_id):
    try:
        r = pd.read_pickle(
            DATA_PATH / f"guideline_{guideline_id}_results_detail.pkl"
        ).fillna("nan")
    except FileNotFoundError:
        raise HTTPException(404, "Guideline not found")
    return r


def get_guideline_ids() -> Dict:
    r = requests.get(GUIDELINE_SERVER + "/guideline/list")
    return r.json()


def get_patients_from_guideline(guideline_id) -> List:
    ret = (
        get_guideline_results_summary(guideline_id)
        .reset_index()["pseudo_fallnr"]
        .unique()
    )
    return list(ret)


def request_data(variables: List[str]) -> pd.DataFrame:
    r = requests.post(PATIENTDATA_SERVER + "/patients/", json=variables)

    df = pd.DataFrame(r.json()).set_index("pseudo_fallnr")

    return df


def get_variables_from_guideline(guideline_id: str) -> List:
    return list(get_guideline_results_details(guideline_id)["variable_name"].unique())


@app.get("/guideline/list")
async def get_guideline_list(current_user: User = Depends(get_current_active_user)):
    return get_guideline_ids()


@app.get("/guideline/get/{guideline_id}")
async def get_guideline_results(
    guideline_id: str, current_user: User = Depends(get_current_active_user)
):
    df_summary = get_guideline_results_summary(guideline_id)
    df_detail = get_guideline_results_details(guideline_id)

    return {"summary": df_summary.to_dict(), "detail": df_detail.to_dict()}


@app.get("/patient/list/{guideline_id}")
async def list_patients(
    guideline_id: str, current_user: User = Depends(get_current_active_user)
):
    return get_patients_from_guideline(guideline_id)


@app.get("/patient/get/{guideline_id}")
async def list_patient(
    guideline_id: str, current_user: User = Depends(get_current_active_user)
):
    variables = get_variables_from_guideline(guideline_id)
    print(variables)
    df = request_data(variables)

    return df.to_dict()
