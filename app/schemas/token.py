from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserOut


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class AuthResponse(Token):
    user: UserOut
