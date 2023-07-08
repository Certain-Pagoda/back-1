import pytest
import uuid

#from moto import mock_dynamodb
from src.users.users import create_user, get_user
from tests.testing_fixtures import data_table, dyn_resource, mock_user_data, mock_link_data
from src.links.links import get_user_links, add_user_link, get_links_short_url, remove_user_link, LinkNotFound, update_link, increase_link_visit_count, MissingLinkURL

ENV = "local"
#HOST = "http://localhost:8000"
#moto.dynamodb.urls.url_bases.append(HOST)

pytest_plugins = ('pytest_asyncio',)

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

    link_dict = mock_link_data

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    uuid_str = user.links[0].uuid

    user = add_user_link(
            username="username-1",
            **link_dict
        )
    uuid_str2 = user.links[1].uuid

    links = get_links_short_url("XXXXXX")
    assert len(links) == 2

    ## Check links by short url for user 1
    user = remove_user_link("username-1", uuid_str)

    assert len(user.links) == 1
    assert uuid_str not in [link.uuid for link in user.links]
    assert uuid_str2 in [link.uuid for link in user.links]

def test_remove_link_not_found(data_table, dyn_resource, mock_user_data, mock_link_data):
    
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
    uuid_str = user.links[0].uuid+"X"

    with pytest.raises(LinkNotFound):
        ## Check links by short url for user 1
        user = remove_user_link("username-1", "XXXXXX")

def test_update_user_link_OK(data_table, dyn_resource, mock_user_data, mock_link_data):
    
    ## Add one user to store 2 links
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
    uuid_str = user.links[0].uuid

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
    uuid_str = user.links[0].uuid

    assert user.links[0].visit_count == 0

    user = increase_link_visit_count("username-1", uuid_str)
    assert user.links[0].visit_count == 1
