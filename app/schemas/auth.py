from typing import Annotated

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    usuario: Annotated[str, Field(min_length=1)]
    clave: Annotated[str, Field(min_length=1)]
    bd: Annotated[str, Field(min_length=1, description="Nombre de la BD del cliente")]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    idusuario: int
    usuario: str
    fullname: str
    cia: int
    empresa: str
    db_name: str


class CurrentUserResponse(BaseModel):
    idusuario: int
    usuario: str
    fullname: str
    cia: int
    empresa: str
    db_name: str
