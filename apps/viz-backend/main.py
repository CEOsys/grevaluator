import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from config import settings
import yaml

BASE_PATH = Path(os.getenv("CEOSYS_BASE_PATH")) / "data"  # type: ignore
DATA_PATH = Path(os.getenv("CEOSYS_DATA_PATH"))  # type : ignore

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


@app.on_event("startup")
async def startup_event():
    data["patients"] = pd.read_pickle(BASE_PATH / "sample_data_shuffle_large.pkl.gz")


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/")
async def root():
    return {"message": "Patient Viz Server"}


@app.get("/guideline/get/{guideline_id}")
async def get_guideline_results(
    guideline_id: str, current_user: User = Depends(get_current_active_user)
):
    return pd.from_pickle(DATA_PATH / f"guideline_{guideline_id}_results.pkl")


@app.get("/patient/list/")
async def list_patients(current_user: User = Depends(get_current_active_user)):
    ret = data["patients"]["pseudo_fallnr"].unique()
    return list(ret)


@app.get("/patient/get/{fallnr}")
async def list_patient(
    fallnr: str, current_user: User = Depends(get_current_active_user)
):
    patient = data["patients"].query("pseudo_fallnr==@fallnr")

    if len(patient) == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient.fillna("").to_dict(orient="list")
