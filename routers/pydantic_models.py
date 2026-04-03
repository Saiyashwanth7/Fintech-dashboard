from pydantic import BaseModel,Field,EmailStr
from typing import Annotated,Optional
from datetime import date
from models import TransactionType,UserRoles


class TransactionRequest(BaseModel):
    amount : float=Field(gt=0)
    type : TransactionType
    category : str
    date : date
    notes : str=None
    
class UserRequest(BaseModel):
    name : str
    email : EmailStr
    password : str
    role : UserRoles = UserRoles.viewer

class TransactionUpdateRequest(BaseModel):
    amount : float=Field(gt=0)
    type : TransactionType
    category : str
    date : date
    notes : str=None

class UserUpdateRequest(BaseModel):
    name : str
    email : EmailStr
    role : UserRoles = UserRoles.viewer
