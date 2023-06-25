import aiohttp
import asyncio
from typing import Dict

from jose import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer

from src.users.users import create_user, get_user

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
    required_fields = ["userName", "email"]
    for field in required_fields:
        if field not in user_data:
            raise Exception(f"Missing {field}")
    
    ## Check if email is not already in the database
    user = get_user(email=user_data["email"])

    user = create_user(
            username=user_data["userName"], 
            email=user_data["email"], 
        )
    
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
        return dict(user=user)

    except Exception as e:
        log.error(e)
        log.error("User error")
        raise Exception("Invalid user")
