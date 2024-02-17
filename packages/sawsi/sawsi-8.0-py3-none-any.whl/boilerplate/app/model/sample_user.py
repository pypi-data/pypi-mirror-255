"""
This is sample code to tell how to use sawsi framework.
You could delete this file after know how to use this framework.
"""

import time
import uuid
from pydantic import BaseModel, fields
from typing import Optional, Literal


class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    id: str = fields.Field(default_factory=lambda: str(uuid.uuid4()))
    crt:float = fields.Field(default_factory=time.time)
    ptn:str = 'user'
    name: str
    age: int
    gender: Optional[Literal["male", "female"]] = None
    address: Address



if __name__ == '__main__':
    # 모델 인스턴스 생성
    address_data = {'street': '123 Main St', 'city': 'Anytown', 'country': 'USA'}
    user_data = {'name': 'John Doe', 'age': 30, 'gender': 'male', 'address': address_data}
    user = User(**user_data)
    print('user.id', user.id)

    # 모델을 딕셔너리로 변환
    user_dict = user.model_dump()
    print(user_dict)