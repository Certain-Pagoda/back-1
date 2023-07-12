import aiohttp
import asyncio
from typing import Dict

from jose import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer

from src.users.users import create_user, get_user
from src.users.user_types import CognitoUserIN

from src.utils.logger import create_logger
log = create_logger(__name__)

from src.auth.cognito_helpers import get_cognito_public_keys, get_hmac_key, verify_token

http_bearer_scheme = HTTPBearer()


def create_user_dict(
        user_data: Dict
        ):
    """ Create a user from the cognito hook
    - TODO: make call fail if the emai it's not unique
    """
    log.info("Creating user")
    cognito_user = CognitoUserIN(**user_data)
    user = create_user(cognito_user)
    return user

## Depends function
async def get_current_user(
        token_dict: str = Depends(http_bearer_scheme)
    ):
    """ Verify the token and get user informatino from the database
    """
    ## verify token
    try:
        payload = await verify_token(token_dict)
    except Exception as e:
        log.error(e)
        log.error("Invalid token")
        raise Exception("Invalid token")
    
    ## Recover user from database
    try:
        print(payload)
        user = get_user(username=payload["username"])
        return user

    except Exception as e:
        log.error(e)
        log.error("User error")
        raise Exception("Invalid user")
