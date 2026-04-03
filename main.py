from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from typing import Annotated

from database import engine,SessionLocal
import models
from models import *
from routers.finance import router as record_router
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.dashboard import router as dashboard_router


models.Base.metadata.create_all(bind=engine)

app=FastAPI()
app.include_router(auth_router)
app.include_router(record_router)
app.include_router(users_router)
app.include_router(dashboard_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
db_dependency=Annotated[Session,Depends(get_db)]

@app.get('/')
def read(db:db_dependency):
    return db.query(Users).all()