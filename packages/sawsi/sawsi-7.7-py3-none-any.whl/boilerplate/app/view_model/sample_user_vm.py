"""
This is sample code to tell how to use sawsi framework.
You could delete this file after know how to use this framework.
"""
from ..model.sample_user import User


def make(user:User)->dict:
    """
    Show information only client can see
    :param user:
    :return:
    """
    return {
        'name': user.name,
        'age': user.age,
    }