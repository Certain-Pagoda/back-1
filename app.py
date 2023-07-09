from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse

from src.auth import auth_api
from src.users import users_api
from src.links import links_api

from typing import Dict

from src.models.dynamoDB.db_connection import InitDB
from src.auth.auth_functions import get_current_user
from src.links.links import follow_link

from src.utils.logger import create_logger
log = create_logger(__name__)

InitDB()

log.info("Tables init")
log.info("App init")

app = FastAPI()

app.include_router(auth_api.router)
app.include_router(users_api.router)
app.include_router(links_api.router)

@app.get("/")
async def root():
    return {"message": "OK"}

@app.get("/{short_url}")
async def follow_url(
        short_url: str
        ) -> RedirectResponse:
    """ Redirect to the link associated with the short url
    """
    link_url = follow_link(short_url)
    return RedirectResponse(link_url)

@app.get("/ping")
async def root(
        request: Request, 
        user: Dict = Depends(get_current_user)
        ):
    print(request)
    return {"message": "Pong!!!"}
