from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute, ListAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

import os

ENV = os.getenv("ENV", "local")
HOST = os.getenv("HOST", "http://localhost:8000")
REGION = os.getenv("REGION", "eu-west-1")

print(f"ENV: {ENV}")

class EmailIndex(GlobalSecondaryIndex):

    class Meta:
        index_name = "email_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)

class User(Model):

    class Meta:
        table_name = f"user-{ENV}"
        host = HOST
        region = REGION
    
    username = UnicodeAttribute(hash_key=True)
    email_index = EmailIndex()
    email = UnicodeAttribute()

