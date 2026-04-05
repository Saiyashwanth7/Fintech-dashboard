from fastapi import FastAPI
from database import engine
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

@app.get('/')
def health_check():
    return {'Health Status':'Alive'}