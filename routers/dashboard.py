from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import Field
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import FinancialRecords
from .pydantic_models import TransactionRequest, TransactionUpdateRequest
from .auth import get_current_user
from collections import defaultdict


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", status_code=status.HTTP_200_OK)
async def dashboard_summary(user: user_dependency, db: db_dependency):
    if user.get("role") == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins and Analysts"
        )
    total_expense = 0
    total_income = 0
    transactions = (
        db.query(FinancialRecords).filter(FinancialRecords.is_deleted == False).all()
    )
    for record in transactions:
        if record.type == "income":
            total_income += record.amount
        elif record.type == "expense":
            total_expense += record.amount
    net_balance = total_income - total_expense
    return {
        "total income": total_income,
        "total expense": total_expense,
        "net balance": net_balance,
    }


@router.get("/by-category", status_code=status.HTTP_200_OK)
async def read_by_category(user: user_dependency, db: db_dependency):
    if user.get("role") == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins and Analysts"
        )
    category_balance = defaultdict(int)
    transactions = (
        db.query(FinancialRecords).filter(FinancialRecords.is_deleted == False).all()
    )
    for record in transactions:
        if record.type.lower() == "income":
            category_balance[record.category.lower()] += record.amount
        elif record.type.lower() == "expense":
            category_balance[record.category.lower()] += record.amount
    return category_balance
