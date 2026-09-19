from datetime import datetime, timedelta, timezone
from fastapi import Depends, APIRouter, HTTPException

from sqlalchemy.orm import Session
from Database import session
from starlette import status
from Database import User
import Database
from typing import Annotated
from pydantic import BaseModel
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
    username : str
    password: str
    email : str

class Token(BaseModel):
    accessToken : str
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
        Database.User.username == create_user_request.username
    ).first()

    if existing_user:
        raise HTTPException(status_code= 400, detail = "User already Register")

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

    user = db.query(Database.User).filter(
        Database.User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(status_code= 401, detail= "Invalid Credentilas")

    if not bcrypt_context.verify(form_data.password , user.password):
        raise HTTPException(status_code= 401, detail = "Invalid Credntial")

    token = create_access_token(user.username)

    return{
        "access_token": token ,
        "token_type" : "bearer"
    }


def create_access_token(username : str) :
    payload = {
        "sub" : username,
        "exp" : datetime.now(datetime.timezone.utc) + timedelta(minutes = 30)
    }

    return jwt.encode(payload, {os.environ.get('SECRET_KEY')}, algorithm = Algorihtm)


async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token,  {os.environ.get('SECRET_KEY')}, algorithms=[Algorihtm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(Database.User).filter(Database.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

