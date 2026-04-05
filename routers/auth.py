from fastapi import APIRouter,Depends,HTTPException
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext
from database import get_db
from models import Users,UserRoles
from .pydantic_models import UserRequest
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from config import SECRET_KEY,ALGORITHM



router = APIRouter(prefix='/auth',tags=['auth'])

db_dependency = Annotated[Session,Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def authenticate_user(username,password,db):
    user_model = db.query(Users).filter(Users.email==username).first()
    if not user_model:
        return False
    if not bcrypt_context.verify(password,user_model.hashed_password):
        return False
    return user_model

def create_access_token(username:str,user_id:int,user_role:str,expires_delta:timedelta):
    encode = {'sub':username,'id':user_id,'role':user_role}
    expires=datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,ALGORITHM)

async def get_current_user(token : Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str = payload.get('sub')
        id:int = payload.get('id')
        role: str = payload.get('role')
        if not email or not id or not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid username or id')
        return {'email':email,'id':id,'role':role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid username or id')

@router.post('/')
async def create_user(user_request: UserRequest, db:db_dependency):
    user_model = db.query(Users).filter(Users.email == user_request.email).first()
    if user_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Email already registered')
    new_user = Users(
        name= user_request.name,
        email= user_request.email,
        hashed_password= bcrypt_context.hash(user_request.password),
        role = user_request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "email": new_user.email}


@router.post('/token')
async def login_for_token(db:db_dependency,form:Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = authenticate_user(form.username,form.password,db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials'
        )
    return {
        'access_token': create_access_token(user.email, user.id, user.role, timedelta(hours=1)),
        'token_type': 'bearer'
    }