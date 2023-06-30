from fastapi import APIRouter, Depends, HTTPException
from src.auth.auth_functions import get_current_user

from src.models.dynamoDB.users import User
from src.users.users import create_user

from src.utils.logger import create_logger
log = create_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/dict_signup")
async def POST_dict_signup(
        user_data: dict
    ):
    """ Function to handle the signup from the cognito pool
    """
    try:
        user = create_user(**user_data)
        log.info(f"User created: {user}")
        return dict(message="OK")
    except Exception as e:
        log.error(e)
        raise HTTPException("Error registering user")
