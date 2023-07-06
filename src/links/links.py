import datetime

from src.users.users import get_user
from src.models.dynamoDB.users import LinkAttributeMap
from src.models.dynamoDB.users import User

def add_user_link(
        username: str,
        **kwargs
        ):
    """ Add a link to the user
    """

    link = LinkAttributeMap(
            url = kwargs['url'],
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
    """

    return None


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
