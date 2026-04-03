from typing import Annotated

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: Annotated[str, Field(min_length=1)]
    password: Annotated[str, Field(min_length=1)]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    idusuario: int
    usuario: str
    fullname: str
