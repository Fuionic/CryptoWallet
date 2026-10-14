from datetime import datetime, timedelta, timezone
from fastapi import Depends, APIRouter, HTTPException

from sqlalchemy.orm import Session
from Database import session
from starlette import status
import Database
from pydantic import BaseModel, Field, field_validator
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os

router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)


Algorihtm = 'HS256'

bcrypt_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl= 'auth/token')

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8)
    email: str = Field(min_length=3, max_length=254)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be no longer than 72 UTF-8 bytes")
        return password

class Token(BaseModel):
    access_token : str
    token_type : str


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code = status.HTTP_201_CREATED)
async def create_user( create_user_request: CreateUserRequest, db : Session = Depends(get_db)):

    existing_user = db.query(Database.User).filter(
        (Database.User.username == create_user_request.username)
        | (Database.User.email == create_user_request.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email is already registered")

    hashed_password = bcrypt_context.hash(create_user_request.password)

    create_user_model = Database.User(
        username = create_user_request.username,
        password = hashed_password,
        email = create_user_request.email
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {
        "id": create_user_model.id,
        "username" : create_user_model.username
    }

@router.post("/token")
async def login_user( form_data: OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    if len(form_data.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = db.query(Database.User).filter(
        Database.User.username == form_data.username
    ).first()

    if not user or not user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not bcrypt_context.verify(form_data.password , user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user.username)

    return{
        "access_token": token ,
        "token_type" : "bearer"
    }

def create_access_token(username : str) :
    secret_key = os.environ.get("SECRET_KEY")

    payload = {
        "sub" : username,
        "exp" : datetime.now(timezone.utc) + timedelta(hours=24)
    }

    return jwt.encode(payload, secret_key, algorithm=Algorihtm)


async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    secret_key = os.environ.get("SECRET_KEY")

    try:
        payload = jwt.decode(token, secret_key, algorithms=[Algorihtm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(Database.User).filter(Database.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/me")
async def read_current_user(current_user: Database.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }
