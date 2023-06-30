import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute, ListAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from src.utils.logger import create_logger
log = create_logger(__name__)

from src.utils.env import load_env
load_env(os.getenv('ENV_FILE', './.env.local'))


ENV = os.getenv("ENV", None)
HOST = os.getenv("HOST", None)
REGION = os.getenv("REGION", None)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)

log.info(f"ENV_FILE: {os.getenv('ENV_FILE', './.env.local')}")
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

class User(Model):

    class Meta(ConfigurationMetaclass):
        table_name = f"user-{ENV}"
        host = HOST
        region = REGION
    
    username = UnicodeAttribute(hash_key=True)
    email_index = EmailIndex()
    email = UnicodeAttribute()

