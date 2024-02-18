"""
This is sample code to tell how to use sawsi framework.
You could delete this file after know how to use this framework.
"""
from {{app}}.dao import sample_user_dao
from {{app}}.model.sample_user import User
from {{app}}.view_model import sample_user_vm
from pydantic import validate_call


@validate_call
def login(email:str, password:str):
    return {
        'session_id': '<SESSION_ID>'
    }


@validate_call  # session_id 에 int 등이 등어가면 에러가 레이즈됩니다.
def get_me(session_id:str):
    # Get Data Model from DAO
    user:User = sample_user_dao.get_user_by_session(session_id)
    # Transform to view model
    user_view_model:dict = sample_user_vm.make(user)
    return {
        'user': user_view_model
    }
