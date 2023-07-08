import pytest
import asyncio
import boto3
from moto import mock_dynamodb
import os
import uuid

from src.models.dynamoDB.users import User, LinkAttributeMap
import datetime

## pynamo does not play well with moto, see https://github.com/pynamodb/PynamoDB/issues/569
import moto.dynamodb.urls
ENV = "local"
HOST = "http://localhost:8000"
moto.dynamodb.urls.url_bases.append(HOST)

pytest_plugins = ('pytest_asyncio',)

#@pytest.fixture
#def env_variables():
#    os.environ["ENV"] = "local"
#

@pytest.fixture
def data_table():
    """ 
    - This can be done yielding a table/tables or decorating the functions and 
    creating the needed tables inside the funcitons
    """
    with mock_dynamodb():
        table = User.create_table(
                read_capacity_units=1, 
                write_capacity_units=1, 
                wait=True)
        yield table

@pytest.fixture
def dyn_resource():
    resource = boto3.resource('dynamodb')
    return resource

@pytest.fixture
def mock_user_data():
    """ Data coming from pre-register webhook trigger
    """
    user_data = {
            'version': '1',
            'region': 'eu-west-1',
            'userPoolId': 'eu-west-1_83vVpEPcH',
            'userName': 'e546e9e2-3afc-4966-bffc-b4713058ae11',
            'callerContext': {'awsSdkVersion': 'aws-sdk-unknown-unknown',
             'clientId': '73ijtu61grkcm8ikel71cfb8vt'},
            'triggerSource': 'PreSignUp_SignUp',
            'request': {'userAttributes': {'email': 'gintonic@gmail.com'},
             'validationData': None},
            'response': {'autoConfirmUser': False,
             'autoVerifyEmail': False,
             'autoVerifyPhone': False}
        }
    return user_data

@pytest.fixture
def mock_link_data():
    """ Link generation
    """
    link_dict = dict(
            url = "https://www.google.com",
            title = "Google",
            description = "Google search engine",
            image_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
            visit_count = 0,
            created_at = datetime.datetime.now(),
            updated_at = datetime.datetime.now(),
            valid_from = datetime.datetime.now(),
            valid_until = datetime.datetime.now() + datetime.timedelta(days=1),
            active = True
        )
    return link_dict
