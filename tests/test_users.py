
import pytest
import asyncio
import boto3
from moto import mock_dynamodb
import os
import uuid

from src.users.users import create_user, get_user
from src.users.users import UserDoesNotExist, MultipleUsersFound, EmailAlreadyExists
from src.models.dynamoDB.users import User, LinkAttributeMap
import datetime
from src.links.links import get_user_links, add_user_link, get_links_short_url, remove_user_link, LinkNotFound, update_link, increase_link_visit_count, MissingLinkURL


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
            uuid = str(uuid.uuid4()),
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

def test_add_user_link_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    """ 2 users with same email are not allowed
    """

    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com",
                links=[]),
                )

    link_dict = mock_link_data

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    
    assert len(user.links) == 1
    assert user.links[0].url == link_dict["url"]
    assert user.links[0].title == link_dict["title"]
    assert user.links[0].description == link_dict["description"]
    assert user.links[0].image_url == link_dict["image_url"]
    assert user.links[0].visit_count == link_dict["visit_count"]
    assert user.links[0].created_at.minute == link_dict["created_at"].minute
    assert user.links[0].updated_at.minute == link_dict["updated_at"].minute
    assert user.links[0].valid_from.minute == link_dict["valid_from"].minute
    assert user.links[0].valid_until.minute == link_dict["valid_until"].minute
    assert user.links[0].active == link_dict["active"]
    assert user.links[0].uuid is not None

def test_add_link_missing_url_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    """ 2 users with same email are not allowed
    """

    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com",
                links=[]),
                )

    link_dict = mock_link_data
    link_dict.pop("url")

    with pytest.raises(MissingLinkURL) as e_link_url:
        user = add_user_link(
                username="username-1",
                **link_dict
            )

def test_add_multiple_link_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    """ 2 users with same email are not allowed
    """
    
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com", 
                links=[]),
                )
    
    link_dict = mock_link_data

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    user = add_user_link(
            username="username-1",
            **link_dict
        )
    assert len(user.links) == 2

def test_get_links_short_url_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    
    link_dict = mock_link_data

    ## Add one user to store 2 links
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com", 
                short_url="XXXXXX",
                links=[]),
                )
    
    user = add_user_link(
            username="username-1",
            **link_dict
        )
    user = add_user_link(
            username="username-1",
            **link_dict
        )

    ## Add one link to another user
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-2",
                email="useremail2@email.com", 
                short_url="XXXXXXY",
                links=[]),
                )

    user = add_user_link(
            username="username-2",
            **link_dict
        )
    
    ## Check links by short url for user 1
    links = get_links_short_url("XXXXXX")
    assert len(links) == 2
    
    ## Check links by short url for user 2
    links = get_links_short_url("XXXXXXY")
    assert len(links) == 1

def test_remove_link_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    


    ## Add one user to store 2 links
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com", 
                short_url="XXXXXX",
                links=[]),
                )

    uuid_str = str(uuid.uuid4())
    link_dict = mock_link_data
    link_dict["uuid"] = uuid_str

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    
    uuid_str2 = str(uuid.uuid4())
    link_dict["uuid"] = uuid_str2
    user = add_user_link(
            username="username-1",
            **link_dict
        )

    links = get_links_short_url("XXXXXX")
    assert len(links) == 2

    ## Check links by short url for user 1
    user = remove_user_link("username-1", uuid_str)

    assert len(user.links) == 1
    assert uuid_str not in [link.uuid for link in user.links]
    assert uuid_str2 in [link.uuid for link in user.links]

def test_remove_link_not_found(data_table, dyn_resource, mock_user_data, mock_link_data):
    
    uuid_str2 = str(uuid.uuid4())
    link_dict = mock_link_data
    link_dict["uuid"] = uuid_str2
    ## Add one user to store 2 links
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com", 
                short_url="XXXXXX",
                links=[]),
                )
    

    user = add_user_link(
            username="username-1",
            **link_dict
        )

    with pytest.raises(LinkNotFound):
        ## Check links by short url for user 1
        user = remove_user_link("username-1", "XXXXXX")

def test_update_user_link_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    
    ## Add one user to store 2 links
    link_dict = mock_link_data
    uuid_str = str(uuid.uuid4())
    link_dict["uuid"] = uuid_str

    ## Add one user to store 2 links
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com", 
                short_url="XXXXXX",
                links=[]),
                )

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    
    ## Update attributes one by one
    user = update_link(
            username="username-1",
            link_uuid=uuid_str, 
            active=False
        ) 

    user = update_link(
            username="username-1",
            link_uuid=uuid_str, 
            title="new titulin"
        ) 

    user = update_link(
            username="username-1",
            link_uuid=uuid_str, 
            url="https://www.yahoo.com"
        ) 
     
    assert user.links[0].active == False
    assert user.links[0].title == "new titulin"
    assert user.links[0].url == "https://www.yahoo.com"

    ## Update multiple attributes
    user = update_link(
            username="username-1",
            link_uuid=uuid_str, 
            active=True,
            url="https://www.bing.com",
            title="titulin2"
        ) 
     
    assert user.links[0].active == True
    assert user.links[0].title == "titulin2"
    assert user.links[0].url == "https://www.bing.com"

def test_increase_visit_count_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    ## Add one user to store 2 links
    link_dict = mock_link_data
    uuid_str = str(uuid.uuid4())
    link_dict["uuid"] = uuid_str

    ## Add one user to store 2 links
    dyn_resource.Table(f"user-{ENV}")\
            .put_item(Item=dict(
                username="username-1",
                email="useremail@email.com", 
                short_url="XXXXXX",
                links=[]),
                )

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    
    assert user.links[0].visit_count == 0

    user = increase_link_visit_count("username-1", uuid_str)
    assert user.links[0].visit_count == 1
