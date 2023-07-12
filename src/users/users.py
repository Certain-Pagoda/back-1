import boto3

from src.models.dynamoDB.users import User
from src.users.user_types import CognitoUserIN
from pynamodb.exceptions import DoesNotExist

class UserCreationError(Exception):
    pass

class UserDoesNotExist(Exception):
    pass

class MultipleUsersFound(Exception):
    pass

class EmailAlreadyExists(Exception):
    pass

def create_user(
        **kwargs
    ):
    """ Add a user coming from cognito to dynamoDB
    
    Create the use rin dynamoDB from the cognito trigger.

    - Kwargs it the dict coming from the cognito trigger
    - Blocking trigger from cognito (before-create) via a lambda
    - cognito --> lambda (relay) --> dict_signup endpoint
    """
    cognito_user = CognitoUserIN(**kwargs)
    username = cognito_user.userName
    email = cognito_user.request.userAttributes.email 
    
    ## Check email is not already taken
    try:
        user = get_user(email=email)
        raise EmailAlreadyExists()
    except UserDoesNotExist:
        pass

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
    if 'email' in kwargs:
        user = [u for u in User.email_index.query(kwargs['email'])]
        print(user)
        if len(user) == 0: 
            raise UserDoesNotExist()
        elif len(user) > 1: 
            raise MultipleUsersFound()
        else:
            return user[0]

    elif 'username' in kwargs:
        try:
            user = User.get(kwargs['username'])
        except DoesNotExist as e:
            raise UserDoesNotExist()
    else:
        raise Exception("Missing email or username")
    
    return user


def update_user(uid, **kwargs):
    """
    """
    return NotImplementedError()

