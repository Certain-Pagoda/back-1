from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, MapAttribute, ListAttribute

import os

ENV = os.getenv("ENV", "local")
HOST = os.getenv("HOST", "http://localhost:8000")
REGION = os.getenv("REGION", "eu-west-1")

print(f"ENV: {ENV}")

class User(Model):

    class Meta:
        table_name = f"user-{ENV}"
        host = HOST
        region = REGION
    
    uid = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    username = UnicodeAttribute()
   
