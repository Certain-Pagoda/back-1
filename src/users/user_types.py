from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import datetime

from src.links.link_types import LinkOUT

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
