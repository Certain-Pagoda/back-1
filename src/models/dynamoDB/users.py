import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute, ListAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pathlib import Path
import random
import string
import uuid

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


class User(Model):

    class Meta(ConfigurationMetaclass):
        table_name = f"user-{ENV}"
        host = HOST
        region = REGION
    
    username = UnicodeAttribute(hash_key=True)
    email_index = EmailIndex()
    email = UnicodeAttribute()

    short_url_index = ShortUrlIndex()
    short_url = UnicodeAttribute(default=''.join(random.choice(string.ascii_lowercase) for i in range(16)))

    links = ListAttribute(of=LinkAttributeMap, default=[])

    def __repr__(self):
        return f"<User {self.username}>"
