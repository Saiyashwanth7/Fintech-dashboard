from fastapi import APIRouter, Depends, HTTPException,Path
from starlette import status
from pydantic import Field
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import FinancialRecords
from .pydantic_models import TransactionRequest, TransactionUpdateRequest
from .auth import get_current_user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/records", tags=["records"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_transactions(user: user_dependency, db: db_dependency):
    return db.query(FinancialRecords).filter(FinancialRecords.is_deleted == False).all()


@router.post("/", status_code=status.HTTP_201_CREATED)  # Admin only
async def create_transaction(
    user: user_dependency, transaction: TransactionRequest, db: db_dependency
):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for Admins"
        )
    new_transaction = FinancialRecords(
        **transaction.model_dump(), created_by=user.get("id")
    )
    db.add(new_transaction)
    db.commit()
    return {"amount": new_transaction.amount, "type": new_transaction.type}


@router.get("/{record_id}", status_code=status.HTTP_200_OK)
async def get_record_by_id(
    user: user_dependency, db: db_dependency, record_id: int = Path(gt=0)
):
    record = db.query(FinancialRecords).filter(FinancialRecords.id == record_id).filter(FinancialRecords.is_deleted==False).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction record of id:{record_id} is not found",
        )
    return {
        "Amount": record.amount,
        "created_by": record.created_by,
        "Type": record.type,
        "Notes": record.notes,
        "Category": record.category,
    }


@router.put("/{record_id}/", status_code=status.HTTP_204_NO_CONTENT)  # Admin only
async def update_record(
    user: user_dependency,
    transaction: TransactionRequest,
    db: db_dependency,
    record_id: int = Path(gt=0),
):
    if user.get('role')!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only for Admins')
    
    record = db.query(FinancialRecords).filter(FinancialRecords.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction record of id:{record_id} is not found",
        )
    record.amount = transaction.amount
    record.category = transaction.category
    record.notes = transaction.notes
    record.date = transaction.date
    record.type = transaction.type
    db.add(record)
    db.commit()
    db.refresh(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record_by_id(
    user: user_dependency, db: db_dependency, record_id: int = Path(gt=0)
):
    if user.get('role')!='admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only for Admins')
    
    record = db.query(FinancialRecords).filter(FinancialRecords.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction record of id:{record_id} is not found",
        )
    record.is_deleted = True  # soft delete instead of actual deletion
    db.add(record)
    db.commit()
    db.refresh(record)
