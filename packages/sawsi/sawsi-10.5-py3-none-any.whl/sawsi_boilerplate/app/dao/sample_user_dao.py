"""
This is sample code to tell how to use sawsi framework.
You could delete this file after know how to use this framework.
"""

import api
from {{app}}.model.sample_user import User


def get_user_by_session(session_id:str)->User:
    address_data = {'street': '123 Main St', 'city': 'Anytown', 'country': 'USA'}
    user_data = {'name': 'John Doe', 'age': 30, 'gender': 'male', 'address': address_data}
    user = User(**user_data)
    return user
