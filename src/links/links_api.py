from fastapi import APIRouter, Depends, HTTPException

from src.auth.auth_functions import get_current_user
from src.models.dynamoDB.users import User
from src.links.links import add_user_link, remove_user_link, update_link, get_links_short_url
from src.links.link_types import LinkIN, LinkOUT

router = APIRouter(
    prefix="/links",
    tags=["links"],
)

@router.post("/")
def POST_create_link(
        link_data: LinkIN,
        user: dict = Depends(get_current_user)
        ):
    """ Get all links for the logged in user
    TODO: Make async
    """
    try:
        user = add_user_link(user.username, **link_data.dict())
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{link_uuid}")
def DELETE_link(
        link_uuid: str,
        user: dict = Depends(get_current_user)
    ):
    """ Get all links for the logged in user
    """
    try:
        user = remove_user_link(user.username, link_uuid)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{link_uuid}")
async def PUT_user(
        link_uuid: str,
        link_data: LinkIN,
        user: dict = Depends(get_current_user)
    ):
    try:
        user = update_link(user.username, link_uuid, **link_data.dict())
        return {"message": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/short_url/{short_url}")
async def GET_links_short_url(
        short_url: str,
    ):
    try:
        links = get_links_short_url(short_url)
        return {"links": links}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
