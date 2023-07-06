from fastapi import APIRouter, Depends, HTTPException

from src.auth.auth_functions import get_current_user
from src.models.dynamoDB.users import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
async def GET_user_links(
        user: dict = Depends(get_current_user)
    ):
    """ Get all links for the logged in user
    """
    user = User.get(user['email'])
    return {"message": user.links}


@router.put("/")
async def PUT_user(
        user: dict = Depends(get_current_user)
    ):
    return {"message": user}
