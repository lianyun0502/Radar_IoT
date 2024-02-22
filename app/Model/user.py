from pydantic import BaseModel, Field, EmailStr
from time import time


class User(BaseModel):
    '''
    User Schema
    '''
    id: str = Field(..., example="John", max_length=50)
    email: str = Field(..., example="john@mail.com", max_length=50)
    phone: str = Field(..., example="0912345670",  max_length=50)
    address: str = Field(..., example="台北市大安區復興南路一段390號", max_length=50)
    

class CreateUser(User):
    '''
    Create User Schema
    '''
    password: str = Field(..., example="password", max_length=50)


class OutUser(User):
    '''
    Out User Schema
    '''


