from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import RedirectResponse

from src.auth.auth_functions import get_current_user
from src.models.dynamoDB.users import User
from src.links.links import add_user_link, remove_user_link, update_link, get_links_short_url, follow_link, upload_image

from src.links.link_types import LinkIN, LinkOUT
from src.users.user_types import UserOUT

from src.utils.logger import create_logger
log = create_logger(__name__)

router = APIRouter(
    prefix="/link",
    tags=["link"],
)

@router.post("/")
def POST_create_link(
        link_data: LinkIN,
        user: dict = Depends(get_current_user)
        ) -> UserOUT:
    """ Get all links for the logged in user
    TODO: Make async
    """
    try:
        log.info(f"Creating link for user {user.username}")
        user = add_user_link(user.username, **link_data.dict())
        return user.to_pydantic()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{link_uuid}")
def DELETE_link(
        link_uuid: str,
        user: dict = Depends(get_current_user)
        ) -> UserOUT:
    """ Get all links for the logged in user
    """
    try:
        log.info(f"Deleting link {link_uuid} for user {user.username}")
        user = remove_user_link(user.username, link_uuid)
        return user.to_pydantic()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{link_uuid}")
async def PUT_link(
        link_uuid: str,
        link_data: LinkIN,
        user: dict = Depends(get_current_user)
        ) -> UserOUT:
    try:
        log.info(f"Updating link {link_uuid} for user {user.username}")
        user = update_link(user.username, link_uuid, **link_data.dict())
        return user.to_pydantic()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{short_url}")
def GET_follow_short_url(
        short_url: str,
        ):
    """ Given a link uuid, redirect to the link's url
    """
    print(f"Getting link short_url {short_url}")
    link_url = follow_link(short_url)
    return RedirectResponse(link_url)

@router.post("/upload_image/{link_uuid}")
def POST_upload_image(
        link_uuid: str,
        image: UploadFile = File(...),
        user: dict = Depends(get_current_user)
        ):
    """ Upload an image to the user's s3 bucket
    """
    file = upload_image(user.username, link_uuid, image)
    return dict(message="Image uploaded successfully")
