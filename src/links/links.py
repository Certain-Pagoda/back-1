import datetime

from src.users.users import get_user
from src.models.dynamoDB.users import LinkAttributeMap
from src.models.dynamoDB.users import User

from src.utils.logger import create_logger
log = create_logger(__name__)

class LinkNotFound(Exception):
    pass

class MissingLinkURL(Exception):
    pass

def add_user_link(
        username: str,
        **kwargs
        ):
    """ Add a link to the user
    """
    if 'url' not in kwargs:
        raise MissingLinkURL()

    link = LinkAttributeMap(
            url = kwargs['url'],
            uuid = kwargs['uuid'],
            title = kwargs['title'],
            description = kwargs['description'],
            image_url = kwargs['image_url'],
            visit_count = kwargs['visit_count'],
            created_at = datetime.datetime.now(),
            updated_at = datetime.datetime.now(),
            valid_from = kwargs['valid_from'],
            valid_until = kwargs['valid_until'],
            active = kwargs['active']
        )

    User(username=username).update(actions=[
        User.links.set(
                User.links.append([link])
            )
        ]
    )
    user = User.get(username)
    return user

def remove_user_link(
        username: str,
        link_uuid: str,
        **kwargs
        ):
    """ Remove a link from the user
    TODO: This operation is not atomic??. It is possible that the link is removed
    """
    links = User.get(username).links
    index = [i for i, link in enumerate(links) if link.uuid == link_uuid]
    if not index:
        raise LinkNotFound(f"Link with uuid {link_uuid} not found")
    index = index[0]
    User(username=username).update(actions=[
            User.links[index].remove()
        ]
    )
    user = User.get(username)
    return user

def get_user_links(
        username: str
        ):
    """ Get all links for the logged in user
    """
    user = get_user(username=username)
    return user.links

def get_links_short_url(
        short_url: str
        ):
    """ Get all links for the short url
    TODO: make sure there is only one user with this short_url
    """
    ## Get user by short_url
    links = [link for user in User.short_url_index.query(short_url) for link in user.links]
    return links

def update_link(
        username: str,
        link_uuid: str,
        **kwargs
        ):
    """ Update a link from the user
    TODO: this operation is not atomic
    """ 
    links = User.get(username).links
    index = [i for i, link in enumerate(links) if link.uuid == link_uuid]
    if not index:
        raise LinkNotFound(f"Link with uuid {link_uuid} not found")
    index = index[0]
    
    ## update link info 
    link = User.get(username).links[index]
    for key, value in kwargs.items():
        if hasattr(link, key):
            setattr(link, key, value)
    
    ## Replace the link
    User(username=username).update(actions=[
            User.links[index].set(link)
        ]
    )
    user = User.get(username)
    return user

def increase_link_visit_count(
        username: str,
        link_uuid: str
        ):
    """ Increase the visit count for the link
    """

    links = User.get(username).links
    index = [i for i, link in enumerate(links) if link.uuid == link_uuid]
    if not index:
        raise LinkNotFound(f"Link with uuid {link_uuid} not found")
    index = index[0]

    User(username=username).update(actions=[
            User.links[index].visit_count.add(1)
        ]
    )
    user = User.get(username)

    return user
