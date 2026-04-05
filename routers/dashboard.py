from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import Field
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
from models import FinancialRecords
from .pydantic_models import TransactionRequest, TransactionUpdateRequest
from .auth import get_current_user
from collections import defaultdict
from sqlalchemy import extract, func


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
    category_balance = defaultdict(lambda : {'income':0,'expense':0})
    transactions = (
        db.query(FinancialRecords).filter(FinancialRecords.is_deleted == False).all()
    )
    for record in transactions:
        cat = record.category.lower()
        if record.type == 'income':
            category_balance[cat]['income'] += record.amount
        else:
            category_balance[cat]['expense'] +=record.amount
    return category_balance


@router.get("/trends", status_code=status.HTTP_200_OK)
async def read_by_trends(user: user_dependency, db: db_dependency):
    if user.get("role") == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins and Analysts"
        )
    results = (
        db.query(
            func.strftime("%Y-%m", FinancialRecords.date).label(
                "month"
            ),  # Here Y should be upper and m should be lower or else M is minutes and y is considered a 2 digit number
            FinancialRecords.type,
            func.sum(FinancialRecords.amount).label("total"),
        )
        .filter(FinancialRecords.is_deleted == False)
        .group_by("month", FinancialRecords.type)
        .order_by("month")
        .all()
    )

    trends = defaultdict(lambda: {"income": 0, "expense": 0})
    for row in results:
        trends[row.month][row.type] += row.total

    return dict(sorted(trends.items()))


@router.get("/recents", status_code=status.HTTP_200_OK)
async def recent_records(user: user_dependency, db: db_dependency):
    if user.get("role") == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins and Analysts"
        )
    return (
        db.query(FinancialRecords)
        .filter(FinancialRecords.is_deleted == False)
        .order_by(FinancialRecords.created_at.desc())
        .limit(10)
        .all()
    )
