from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    access_token: str 
    token_type: str


class TokenData(BaseModel):
    username: Optional[str]= Field(None, description="使用者名稱")