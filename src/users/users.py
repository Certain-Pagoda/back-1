import boto3

from src.models.dynamoDB.users import User
from pynamodb.exceptions import DoesNotExist

class MissingUserUsername(Exception):
    pass

class MissingUserEmail(Exception):
    pass

class UserCreationError(Exception):
    pass

class UserDoesNotExist(Exception):
    pass

def create_user(
        **kwargs
    ):
    """ Add a user coming from cognito to dynamo

    - Kwargs it the dict coming from the cognito trigger
    - Blocking trigger from cognito (before-create) via a lambda
    - cognito --> lambda (relay) --> dict_signup endpoint

    TODO: 
    """
    if 'userName' not in kwargs:
        raise MissingUserUsername()
    username = kwargs['userName']

    if 'request' not in kwargs and 'userAttributes' not in kwargs['request'] and 'email' not in kwargs['request']['userAttributes']:
        raise MissingUserEmail()
    email = kwargs['request']['userAttributes']['email']

    try:
        user = User(
                email=email,
                username=username
        )
        user.save()

        return user

    except Exception as e:
        raise UserCreationError(e)

def get_user(
        **kwargs
    ):
    """ Get the user from the database

    """


    try:
        if 'email' in kwargs:
            user = User.email_index.get(kwargs['email'])
        elif 'username' in kwargs:
            user = User.get(kwargs['username'])
        else:
            raise Exception("Missing email or username")

        return user

    except DoesNotExist as e:
        raise UserDoesNotExist(e)

    except:
        raise Exception("Error getting the user")

def update_user(uid, **kwargs):
    """
    """
    return NotImplementedError()

