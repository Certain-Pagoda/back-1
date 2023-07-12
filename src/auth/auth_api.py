from fastapi import APIRouter, Depends, HTTPException
from src.auth.auth_functions import get_current_user, create_user_dict

from src.models.dynamoDB.users import User
from src.users.users import create_user
from src.auth.cognito_helpers import exchange_auth_code

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
        user = create_user_dict(user_data)
        log.info(f"User created: {user}")
        return dict(message="OK")
    except Exception as e:
        log.error(e)
        raise HTTPException("Error registering user")

## Oauth2 callback
@router.get("/callback")
async def GET_code_callback(
        code: str
    ):
    """ Function to handle the callback from the oauth function
    """
    ## Exchange the code for a token
    ## This token comes from aws directly via the oauth2 flow in the back
    token = await exchange_auth_code(code)

    ## Check the user exists in the database
    #user = User.get_or_none(User.email == token['email'])

    return dict(token = token)
