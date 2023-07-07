import datetime

from src.users.users import get_user
from src.models.dynamoDB.users import LinkAttributeMap
from src.models.dynamoDB.users import User

class LinkNotFound(Exception):
    pass

def add_user_link(
        username: str,
        **kwargs
        ):
    """ Add a link to the user
    """

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
