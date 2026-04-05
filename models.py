from database import Base,engine
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
)
from datetime import datetime, timezone
from sqlalchemy import Enum as SAEnum
import enum


class UserRoles(str, enum.Enum):
    admin = "admin"
    viewer = "viewer"
    analyst = "analyst"


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(SAEnum(UserRoles), default=UserRoles.viewer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FinancialRecords(Base):
    __tablename__ = "financial_records"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    type = Column(SAEnum(TransactionType))
    category = Column(String)
    date = Column(DateTime)
    notes = Column(String, default="")
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
