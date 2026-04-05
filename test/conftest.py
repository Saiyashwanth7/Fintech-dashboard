from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from models import Base
from main import app
from models import Users,FinancialRecords
from database import get_db
import pytest
from fastapi.testclient import TestClient
from starlette import status
from datetime import datetime

TEST_DB_URL='sqlite:///.test.db'

engine = create_engine(TEST_DB_URL,connect_args={'check_same_thread':False},poolclass=StaticPool)

TestingSessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

Base.metadata.create_all(bind = engine)

def override_get_db():
    db= TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    client = TestClient(app)
    return client

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True, scope='session') #This will delete entire database tables and create new one
def clear_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def admin_as_user(db):
    user = Users(
        name="Amdin User",
        email="admin@gmail.com",
        hashed_password="hashed",
        role="admin"
    )
    db.add(user)
    db.commit()
    yield user          # test runs here
    db.query(Users).delete()  # cleanup after test
    db.commit()
    db.close()

@pytest.fixture
def analyst_as_user(db):
    user = Users(
        name="Analyst User",
        email="analyst@gmail.com",
        hashed_password="hashed",
        role="analyst"
    )
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
    db.close()

@pytest.fixture
def viewer_as_user(db):
    user = Users(
        name="Viewer User",
        email="viewer@gmail.com",
        hashed_password="hashed",
        role="viewer"
    )
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
    db.close()
    
@pytest.fixture
def sample_records(db,admin_as_user):
    records = [
        FinancialRecords(
            amount =100000,
            type = 'income',
            category = 'salary',
            date=datetime(2026,4,5),
            notes= '',
            created_by=1 
        ),
        FinancialRecords(
            amount =28000,
            type = 'income',
            category = 'stocks',
            date=datetime(2026,4,4),
            notes= '',
            created_by=1 
        ),
        FinancialRecords(
            amount =2800,
            type = 'expense',
            category = 'Air fryer',
            date=datetime(2026,4,6),
            notes= '',
            created_by=1 
        ),
        FinancialRecords(
            amount =5000,
            type = 'expense',
            category = 'food',
            date=datetime(2026,4,5),
            notes= '',
            created_by=1 
        )
    ]
    db.add_all(records)
    db.commit()
    yield records
    db.query(FinancialRecords).delete()
    db.commit()
    db.close()