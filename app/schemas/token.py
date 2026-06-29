from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema representing the access token returned on login.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema representing the decoded access token payload.
    """
    sub: Optional[str] = None
