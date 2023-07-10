import datetime
import uuid
import hashlib

from src.users.users import get_user
from src.models.dynamoDB.users import LinkAttributeMap
from src.models.dynamoDB.users import User
from src.utils.s3_bucket import upload_image_s3


from src.utils.logger import create_logger
log = create_logger(__name__)

class LinkNotFound(Exception):
    pass

class MissingLinkURL(Exception):
    pass

def _shorten_url(link_uuid: str) -> str:
    """ Take the uuid and produce a short url
    TODO: change this to something reversible?
    """
    hash = hashlib.sha1(link_uuid.encode("UTF-8")).hexdigest()
    return hash[:10]

def add_user_link(
        username: str,
        **kwargs
        ):
    """ Add a link to the user
    """
    if 'url' not in kwargs:
        raise MissingLinkURL()
    
    link_uuid = str(uuid.uuid4())
    short_url = _shorten_url(link_uuid)
    link = LinkAttributeMap(
            url = kwargs['url'],
            short_url = short_url,
            uuid = link_uuid,
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

def _get_link(
        **kwargs
    ):
    """ Get the link using the uuid or short_url
    """
    if 'uuid' in kwargs:
        link = [link for user in User.scan() for link in user.links if link.uuid == kwargs['uuid']]

    elif 'short_url' in kwargs:
        link = [link for user in User.scan() for link in user.links if link.short_url == kwargs['short_url']]

    else:
        raise Exception("Either uuid or short_url must be provided")

    if not link:
        raise LinkNotFound(f"Link with uuid {kwargs['uuid']} not found")
    return link[0]

def increase_link_visit_count(
        link_uuid: str
        ):
    """ Increase the visit count for the link
    TODO: this is an stupid way to access the links, this needs to be indexed in the database bc is arguiably the most executed operation (search a link by it's shortened url)
    """

    index = [(user, i) for user in User.scan() for i, link in enumerate(user.links) if link.uuid == link_uuid]
    if not index:
        raise LinkNotFound(f"Link with uuid {link_uuid} not found")
    user, index = index[0]

    User(username=user.username).update(actions=[
            User.links[index].visit_count.add(1)
        ]
    )
    user = User.get(user.username)
    return user

def get_links_short_url(
        short_url: str
        ):
    """ Get all links for the short url
    TODO: make sure there is only one user with this short_url
    """
    ## Get user by short_url
    links = [link for user in User.short_url_index.query(short_url) for link in user.links]
    return links

def follow_link(
        short_url: str
        ):
    """ Take the user to the link and do the housekeeping
    """
    print(f"short_url: {short_url}")
    link = _get_link(short_url=short_url)
    print(f"Link: {link}")
    if not link:
        raise LinkNotFound(f"Link with uuid {link_uuid} not found")

    user = increase_link_visit_count(link.uuid)
    return link.url

def upload_image(
        username,
        link_uuid,
        image
        ):
    """ Upload an image to the link
    """
    
    image_url = upload_image_s3(image, link_uuid)

    link = update_link(
            username=username, 
            link_uuid=link_uuid, 
            image_url=image_url
            )

    return link
