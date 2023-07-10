import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute, ListAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pathlib import Path
import random
import string
import uuid

from src.users.user_types import UserOUT
from src.links.link_types import LinkOUT

from src.utils.logger import create_logger
log = create_logger(__name__)

from src.utils.env import load_env
load_env("./.env")

ENV = os.getenv("ENV", None)
HOST = os.getenv("HOST", None)
REGION = os.getenv("REGION", None)

AWS_ACCESS_KEY_ID_FILE = os.getenv("AWS_ACCESS_KEY_ID_FILE" , None)
if AWS_ACCESS_KEY_ID_FILE is not None and Path(AWS_ACCESS_KEY_ID_FILE).is_file():
    log.info("Loading AWS_ACCESS_KEY_ID from file")
    AWS_ACCESS_KEY_ID = open(AWS_ACCESS_KEY_ID_FILE, 'r').read().strip()
else:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)


AWS_SECRET_ACCESS_KEY_FILE = os.getenv("AWS_SECRET_ACCESS_KEY_FILE" , None)
if AWS_SECRET_ACCESS_KEY_FILE is not None and Path(AWS_SECRET_ACCESS_KEY_FILE).is_file():
    log.info("Loading AWS_SECRET_ACCESS_KEY from file")
    AWS_SECRET_ACCESS_KEY = open(AWS_SECRET_ACCESS_KEY_FILE, 'r').read().strip()
else:
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY ", None)


log.info(f"ENV: {ENV}")
log.info(f"HOST: {HOST}")
log.info(f"REGION: {REGION}")
log.info(f"AWS_ACCESS_KEY_ID set: {AWS_ACCESS_KEY_ID is not None}")
log.info(f"AWS_SECRET_ACCESS_KEY set: {AWS_SECRET_ACCESS_KEY is not None}")

class ConfigurationMetaclass:
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY

class EmailIndex(GlobalSecondaryIndex):

    class Meta(ConfigurationMetaclass):
        index_name = "email_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)

class ShortUrlIndex(GlobalSecondaryIndex):

    class Meta(ConfigurationMetaclass):
        index_name = "short_url_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    short_url = UnicodeAttribute(hash_key=True)

class LinkAttributeMap(MapAttribute):
    url = UnicodeAttribute()
    short_url = UnicodeAttribute()
    uuid = UnicodeAttribute(default=str(uuid.uuid4()))
    title = UnicodeAttribute()
    description = UnicodeAttribute()
    image_url = UnicodeAttribute()
    visit_count = NumberAttribute(default=0)
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    valid_from = UTCDateTimeAttribute()
    valid_until = UTCDateTimeAttribute()
    active = BooleanAttribute(default=True)
    
    def __repr__(self):
        return f"<LinkAttributeMap {self.title}: {self.url}>"
    
    def to_pydantic(self):
        return LinkOUT(
            url=self.url,
            short_url=self.short_url,
            uuid=self.uuid,
            title=self.title,
            description=self.description,
            image_url=self.image_url,
            visit_count=self.visit_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
            valid_from=self.valid_from,
            valid_until=self.valid_until,
            active=self.active
        )

class User(Model):

    class Meta(ConfigurationMetaclass):
        table_name = f"user-{ENV}"
        host = HOST
        region = REGION
    
    username = UnicodeAttribute(hash_key=True)
    email_index = EmailIndex()
    email = UnicodeAttribute()
    uuid = UnicodeAttribute(default=str(uuid.uuid4()))

    short_url_index = ShortUrlIndex()
    short_url = UnicodeAttribute(default=''.join(random.choice(string.ascii_lowercase) for i in range(16)))

    links = ListAttribute(of=LinkAttributeMap, default=[])
    
    ## Stripe billing info
    customer_id = UnicodeAttribute(null=True, default=None)
    price_id = UnicodeAttribute(null=True, default=None)
    subscription_id = UnicodeAttribute(null=True, default=None)
    subscription_status = UnicodeAttribute(null=True, default=None)
    subscription_created_at = UTCDateTimeAttribute(null=True, default=None)
    subscription_current_period_start = UTCDateTimeAttribute(null=True, default=None)
    subscription_current_period_end = UTCDateTimeAttribute(null=True, default=None)


    def __repr__(self):
        return f"<User {self.username}>"

    def to_pydantic(self):
        return UserOUT(
            username=self.username,
            uuid=self.uuid,
            email=self.email,
            short_url=self.short_url,
            links= [link.to_pydantic() for link in self.links]
        )

