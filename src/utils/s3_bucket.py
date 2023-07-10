
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path

from src.utils.logger import create_logger
log = create_logger(__name__)

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

log.info(f"AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID is None}")
log.info(f"AWS_SECRET_ACCESS_KEY: {AWS_SECRET_ACCESS_KEY is None}")

def upload_image_s3(
        image,
        uuid
        ):
    """ Upload an image to the link
    """
    if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
        s3_client = boto3.client('s3')#, 
    else:
        s3_client = boto3.client('s3',
            aws_access_key_id=AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    bucket_name = 'links-images-dev'

    try:
        contents = image.file.read()
        image.file.seek(0)
        response = s3_client.upload_fileobj(image.file, bucket_name, uuid)
        log.info(f"Uploaded image to s3: {response}")
        image_url=f"https://{bucket_name}.s3.amazonaws.com/{uuid}"
        return image_url

    except ClientError as e:
        log.error(e)
        return False
