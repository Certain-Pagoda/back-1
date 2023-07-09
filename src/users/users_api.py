from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.auth.auth_functions import get_current_user
from src.users.user_types import UserOUT
from src.links.link_types import LinkOUT

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/", response_model=UserOUT)
async def GET_user(
        user: dict = Depends(get_current_user)
        ) -> UserOUT:
    return user.to_pydantic()

@router.put("/", response_model=UserOUT)
async def PUT_user(
        user: dict = Depends(get_current_user)
    ) -> UserOUT:
    return user.to_pydantic()

@router.get("/{short_url}")
async def GET_links_short_url(
        short_url: str,
        ) -> List[LinkOUT]:
    try:
        log.info(f"Getting links for short_url {short_url}")
        links = get_links_short_url(short_url)
        return [link.to_pydantic() for link in links]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
