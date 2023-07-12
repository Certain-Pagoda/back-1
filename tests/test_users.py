import pytest
import asyncio
import boto3
from moto import mock_dynamodb
import os
import uuid
import pydantic

from src.users.users import create_user, get_user
from src.users.users import UserDoesNotExist, MultipleUsersFound, EmailAlreadyExists
from src.models.dynamoDB.users import User, LinkAttributeMap
import datetime

from src.links.links import get_user_links, add_user_link, get_links_short_url, remove_user_link, LinkNotFound, update_link, increase_link_visit_count, MissingLinkURL

from tests.testing_fixtures import data_table, dyn_resource, mock_user_data

## pynamo does not play well with moto, see https://github.com/pynamodb/PynamoDB/issues/569
import moto.dynamodb.urls
ENV = "local"
HOST = "http://localhost:8000"
moto.dynamodb.urls.url_bases.append(HOST)

## REMEMBER TO SET THE ENVIRONMENT VARIABLES !!!
pytest_plugins = ('pytest_asyncio',)

def test_create_user_OK(data_table, dyn_resource, mock_user_data):

    ## Create user using function
    user = create_user(
               **mock_user_data 
            )
    
    ## CHeck effect getting user directy from the database
    table = dyn_resource.Table(f"user-{ENV}")
    response = table.get_item(Key={'username': user.username})
    assert response['Item']['username'] == user.username
    assert response['Item']['email'] == user.email
    assert response['Item']['short_url'] is not None

    ## Check that empty fields are still created

def test_create_user_no_username_ERROR(data_table, dyn_resource, mock_user_data):
    mock_user_data.pop("userName")
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        user = create_user(
               **mock_user_data 
            )

def test_create_user_no_email_ERROR(data_table, dyn_resource, mock_user_data):
    mock_user_data['request']['userAttributes'].pop("email")
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        user = create_user(
               **mock_user_data 
            )

    mock_user_data['request'].pop("userAttributes")
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        user = create_user(
               **mock_user_data 
            )

    mock_user_data.pop("request")
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        user = create_user(
               **mock_user_data 
            )

def test_create_user_duplicated_email(data_table, dyn_resource, mock_user_data):
    """ Raise and exception when trying to create a user with an email that already exists
    """
    user = create_user(
            **mock_user_data
            )

    with pytest.raises(EmailAlreadyExists):
        user = create_user(
                **mock_user_data
                )


def test_get_user_username_OK(data_table, dyn_resource, mock_user_data):

    dyn_resource\
            .Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username=mock_user_data["userName"], 
                email=mock_user_data["request"]["userAttributes"]["email"]))
    
    user = get_user(
            username = mock_user_data["userName"]
        )
    assert user.username == mock_user_data["userName"]

def test_get_user_email_OK(data_table, dyn_resource, mock_user_data):

    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username=mock_user_data["userName"], 
                email=mock_user_data["request"]["userAttributes"]["email"]))
    
    user = get_user(
            email = mock_user_data["request"]["userAttributes"]["email"]
        )
    assert user.username == mock_user_data["userName"]

def test_user_user_username_UserDoesNotExist(data_table, dyn_resource, mock_user_data):
    
    with pytest.raises(UserDoesNotExist) as e_user:
        user = get_user(
            username = "wrong-username"
        )

def test_user_user_email_UserDoesNotExist(data_table, dyn_resource, mock_user_data):
    
    with pytest.raises(UserDoesNotExist) as e_user:
        user = get_user(
            email = "no-reply@nono.com"
        )
def test_user_user_username_email_Multiple(data_table, dyn_resource, mock_user_data):
    """ 2 users with same email are not allowed
    """
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com"))

    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-2",
                email="useremail@email.com"))

    with pytest.raises(MultipleUsersFound) as e_user:
        user = get_user(
            email = "useremail@email.com",
            )
        print(user)

