from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import datetime

class LinkIN(BaseModel):
    """ Link input model
    """
    url: str
    title: str
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    visit_count: Optional[int] = 0
    created_at: Optional[datetime.datetime] = datetime.datetime.now()
    updated_at: Optional[datetime.datetime] = datetime.datetime.now()
    valid_from: Optional[datetime.datetime] = datetime.datetime.now()
    valid_until: Optional[datetime.datetime] = datetime.datetime(9999, 12, 31)
    active: Optional[bool] = True


class LinkOUT(LinkIN):
    """ Link output model
    """
    uuid: UUID
