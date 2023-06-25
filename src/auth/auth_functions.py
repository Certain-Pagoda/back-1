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
    """
    log.info("Creating user")
    required_fields = ["userName", "email", "sub"]
    for field in required_fields:
        if field not in user_data:
            raise Exception(f"Missing {field}")

    user = create_user(
            username=user_data["userName"], 
            email=user_data["email"], 
            cognito_id=user_data["sub"]
        )
    
    return user

## Depends function
async def get_current_user(
        token_dict: str = Depends(http_bearer_scheme)
    ):
    """ This function getsa a token, makes verifications and returns a user if everything is OK
    """
    try:
        payload = await verify_token(token_dict, jwtk)
        #user = 
        return dict(payload=payload)
    except:
        raise Exception("Invalid token")


