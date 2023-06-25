import aiohttp
import asyncio
import os
from urllib.parse import urljoin

from typing import Dict

import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

from src.utils.logger import create_logger
log = create_logger(__name__)

CLIENT_ID = os.getenv("CLIENT_ID", "73ijtu61grkcm8ikel71cfb8vt")
log.info(f"CLIENT_ID: {CLIENT_ID}")

COGNITO_POOL_ID = os.getenv("COGNITO_POOL_ID", "eu-west-1_83vVpEPcH")
log.info(f"COGNITO_POOL_ID: {COGNITO_POOL_ID}")

REGION = os.getenv("REGION", "eu-west-1")
log.info(f"REGION: {REGION}")

BASE_AUTH_URL = os.getenv("BASE_AUTH_URL", "https://linktree-dev.auth.eu-west-1.amazoncognito.com")
log.info(f"BASE_AUTH_URL: {BASE_AUTH_URL}")

REDIRECT_URL = os.getenv("REDIRECT_URL", "http://localhost:8080/auth/callback/")
log.info(f"REDIRECT_URL: {REDIRECT_URL}")

## Get public keys at the start of the application and store it

def get_cognito_public_keys(
    ):
    """ Get the public keys from the cognito pool

    This function gets the public keys from the cognito pool required to verify the identity token
    
    Returns:
        Dict: The public keys
    """
    log.info("Getting cognito public keys")
    url = f"https://cognito-idp.{REGION}.amazonaws.com/{COGNITO_POOL_ID}/.well-known/jwks.json"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Request error with code {resp.status_code}")
    return resp.json()

JWKS = get_cognito_public_keys()

def get_hmac_key(
        token: str, 
        jwks: Dict
        ) -> Dict:
    """ This function gets the hmac key from the public keys

    Args:
        token (str): The token to verify
        jwks (Dict): The public keys
    Returns:
        Dict: The hmac key
    """
    kid = jwt.get_unverified_header(token).get("kid")
    log.info(f"Getting hmac key for kid {kid}")
    for pkey in jwks['keys']:
        for k, v in pkey.items():
            if k == 'kid' and v == kid:
                return pkey

    raise Exception("Invalid public keys")

async def verify_token(
        token: str,
        ) -> Dict:
    """ This function verifies the token is valid

    Args:
        token (str): The token to verify
        jwks (Dict): The public keys
    Returns:
        Dict: The payload of the token
    Raises:
        Exception: If the token is not valid
    """

    # Check the token is valid
    jwt_token = token.credentials
    header_message, encoded_signature = jwt_token.rsplit(".", 1)
    
    ## Construct key
    hmac_key = jwk.construct(get_hmac_key(jwt_token, JWKS))
    
    decoded_signature = base64url_decode(encoded_signature.encode())
    print(hmac_key.verify(header_message.encode(), decoded_signature))

    if hmac_key.verify(header_message.encode(), decoded_signature):
        return jwt.get_unverified_claims(jwt_token)

    else:
        raise Exception("Invalid token")


async def exchange_auth_code(
        code: str, 
    ):
    """ Exchange auth code for a set of tokens

    Get the callback from the auth page and exchange it for a set of tokens

    Args:
        code (str): The code from the callback url coming from cognito
    Returns:
        Dict: The tokens
    Raises:
        Exception: If the code is not valid or there is a problem with the request
    """
    headers = {}
    data = dict(
            grant_type = "authorization_code",
            code = code,
            client_id = CLIENT_ID,
            redirect_uri = REDIRECT_URL,
            )

    async with aiohttp.ClientSession(headers=headers) as session:

        url = urljoin(BASE_AUTH_URL, '/oauth2/token')
        async with session.post(url, data=data) as rta:
            if rta.status != 200:
                raise Exception("Error exhanging code")
            jresp = await rta.json()
            return jresp

    raise Exception("Error exchangin token")
