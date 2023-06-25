from fastapi import FastAPI, Request, Depends
from src.auth import auth_api
from src.users import users_api

from typing import Dict

from src.models.dynamoDB.db_connection import InitDB
from src.auth.auth_functions import get_current_user

from src.utils.logger import create_logger

log = create_logger(__name__)

InitDB()

log.info("Tables init")
log.info("App init")

app = FastAPI()

app.include_router(auth_api.router)
app.include_router(users_api.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/ping")
async def root(
        request: Request, 
        user: Dict = Depends(get_current_user)
        ):
    print(request)
    return {"message": "Pong1!"}

