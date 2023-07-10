from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
import datetime
from enum import Enum
from datetime import datetime, date


class PriceIN(BaseModel):
    """ Input model for the price
    """
    
    id: str
    product: str
    lookup_key: Optional[str]
    currency: str
    unit_amount: int
    unit_amount_decimal: str
    type: str
    active: bool

class PriceOut(PriceIN):
    """ Output model for the price
    - Do the key transformation
    """
    uuid: UUID


class SubscriptionIN(BaseModel):

    id: str
    ## Identification for the customer
    customer: str
    created: date
    current_period_start: date
    current_period_end: date
    status: str
    price_id: str

class SubscriptionOUT(SubscriptionIN):
    """ Output model for the subscription
    """
    uuid: UUID

class CustomerIN(BaseModel):
    """ Input model for the customer
    """
    id: str
    uuid: UUID
    company_id: int
    created: datetime
