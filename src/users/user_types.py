from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import datetime

from src.links.link_types import LinkOUT

class CallerContext(BaseModel):
    """ Caller context model
    """
    awsSdkVersion: str
    clientId: str

class UserAttributes(BaseModel):
    """ User attributes model
    """
    email: str

class Request(BaseModel):
    """ Request model
    """
    userAttributes: UserAttributes
    validationData: Optional[dict]

class Response(BaseModel):
    """ Response model
    """
    autoConfirmUser: bool
    autoVerifyEmail: bool
    autoVerifyPhone: bool

class CognitoUserIN(BaseModel):
    """ Cognito user input model
    """
    version: str
    region: str
    userPoolId: str
    userName: str
    triggerSource: str
    callerContext: CallerContext
    request: Request
    response: Response

class UserIN(BaseModel):
    """ User input model
    """
    username: str
    email: str
    links: Optional[List] = []
    short_url: Optional[str] = ""


class UserOUT(UserIN):
    """ User output model
    """
    uuid: UUID
    username: str
    email: str

    links: Optional[List[LinkOUT]] = []
    short_url: Optional[str] = ""
    
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None
    #subscription_created_at: Optional[datetime.datetime] = None
    #subscription_current_period_start: Optional[datetime.datetime] = None
    #subscription_current_period_end: Optional[datetime.datetime] = None
