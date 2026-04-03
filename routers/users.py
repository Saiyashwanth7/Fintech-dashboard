from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import Field
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import Users, UserRoles
from .auth import get_current_user
from .pydantic_models import UserUpdateRequest


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/users", tags=["user"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/",status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins"
        )
    return db.query(Users).all()


@router.get("/{user_id}",status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)
):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins"
        )
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"username": user_model.name, "email": user_model.email}


@router.put("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_user_by_id(
    user: user_dependency,
    db: db_dependency,
    user_request: UserUpdateRequest,
    user_id: int = Path(gt=0),
):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins"
        )
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_model.name = user_request.name
    user_model.email = user_request.email
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    
